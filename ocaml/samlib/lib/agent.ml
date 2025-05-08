open Core
open Async

(** Agent message handling interface *)
module type Message_Handler = sig
  type message [@@deriving sexp, show, eq]
  type state
  
  val handle_message : state -> message -> state Deferred.t
end

(** Base agent implementation *)
module Make (H : Message_Handler) = struct
  module Channel = Channel.Make(struct
    type t = H.message [@@deriving sexp, show, eq]
  end)

  type t = {
    channel: Channel.t;
    mutable state: H.state;
    mutable running: bool;
  }

  let create ~initial_state ?(channel_capacity = 64) () =
    { channel = Channel.create ~capacity:channel_capacity ();
      state = initial_state;
      running = false }

  let get_channel t = t.channel

  let stop t =
    t.running <- false;
    Channel.close t.channel

  let run t =
    t.running <- true;
    
    let rec process_messages () =
      if not t.running then
        return ()
      else
        Channel.receive t.channel >>= function
        | None -> return ()
        | Some msg ->
            H.handle_message t.state msg >>= fun new_state ->
            t.state <- new_state;
            process_messages ()
    in
    
    don't_wait_for (process_messages ());
    return t

  let send t msg =
    if t.running then
      Channel.send t.channel msg
    else
      return false
      
  let get_state t = t.state
end

(** Empty state implementation for stateless agents *)
module Empty_State = struct
  type t = unit [@@deriving sexp, show, eq]
  let create () = ()
end
