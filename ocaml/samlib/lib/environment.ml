open Core
open Async

(** Environment configuration *)
type config = {
  default_channel_capacity: int;
  worker_count: int;
} [@@deriving sexp, show]

let default_config = {
  default_channel_capacity = 64;
  worker_count = 4;
}

(** Agent registry for the environment *)
module Agent_Registry = struct
  type t = {
    agents: (string, unit Ivar.t) Hashtbl.t;
    mutable running: bool;
  }

  let create () = {
    agents = Hashtbl.create (module String);
    running = false;
  }

  let register t name =
    let ivar = Ivar.create () in
    Hashtbl.set t.agents ~key:name ~data:ivar;
    ivar

  let unregister t name =
    match Hashtbl.find_and_remove t.agents name with
    | Some ivar -> Ivar.fill_if_empty ivar ()
    | None -> ()

  let stop_all t =
    t.running <- false;
    Hashtbl.iter t.agents ~f:(fun ivar -> Ivar.fill_if_empty ivar ())
end

(** Environment for managing agents *)
type t = {
  config: config;
  registry: Agent_Registry.t;
  scheduler: Scheduler.t;
}

let create ?(config = default_config) () =
  { config;
    registry = Agent_Registry.create ();
    scheduler = Scheduler.create () }

let spawn t (type msg state) 
    (module H : Agent.Message_Handler with type message = msg 
                                     and type state = state)
    ~name ~initial_state =
  let module A = Agent.Make(H) in
  let agent = A.create ~initial_state
      ~channel_capacity:t.config.default_channel_capacity () in
  let stop_signal = Agent_Registry.register t.registry name in
  
  don't_wait_for (
    A.run agent >>= fun _ ->
    Deferred.any [
      (Ivar.read stop_signal >>| fun () -> 
       A.stop agent;
       Agent_Registry.unregister t.registry name);
      (Deferred.never ())
    ]
  );
  agent

let stop t =
  Agent_Registry.stop_all t.registry;
  Scheduler.shutdown t.scheduler ~force:false
