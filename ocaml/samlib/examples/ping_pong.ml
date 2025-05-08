open Core
open Async

(* Message types *)
type ping_message = Ping of int [@@deriving sexp, show, eq]
type pong_message = Pong of int [@@deriving sexp, show, eq]

(* Ping agent *)
module Ping_Handler = struct
  type message = pong_message [@@deriving sexp, show, eq]
  type state = {
    count: int;
    pong_agent: string;
  }

  let handle_message state (Pong count) =
    if count >= 10 then
      return state
    else
      let new_state = { state with count = count + 1 } in
      return new_state
end

(* Pong agent *)
module Pong_Handler = struct
  type message = ping_message [@@deriving sexp, show, eq]
  type state = {
    ping_agent: string;
  }

  let handle_message state (Ping count) =
    return state
end

(* Example usage *)
let run_example () =
  let env = Environment.create () in
  
  (* Create agents *)
  let pong = Environment.spawn env
    (module Pong_Handler)
    ~name:"pong"
    ~initial_state:{ ping_agent = "ping" }
  in
  
  let ping = Environment.spawn env
    (module Ping_Handler)
    ~name:"ping"
    ~initial_state:{ count = 0; pong_agent = "pong" }
  in
  
  (* Start ping-pong *)
  don't_wait_for (
    Clock.after (Time.Span.of_sec 5.0) >>= fun () ->
    Environment.stop env;
    return ()
  );
  
  Deferred.never ()
