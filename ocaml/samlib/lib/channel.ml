open Core
open Async

(** Message type that can be sent through channels *)
module type Message = sig
  type t [@@deriving sexp, show, eq]
end

(** Channel implementation for message passing *)
module Make (M : Message) = struct
  type t = {
    channel : M.t Async.Channel.t;
    mutable closed : bool;
    capacity : int;
  }

  let create ?(capacity = 64) () =
    { channel = Async.Channel.create (); 
      closed = false;
      capacity }

  let send t value =
    if t.closed then
      return false
    else
      (* Use write' to handle backpressure *)
      Async.Channel.write' t.channel value >>= fun () ->
      return true

  let receive t =
    if t.closed && Async.Channel.is_empty t.channel then
      return None
    else
      Async.Channel.read t.channel >>| Option.some

  let try_receive t =
    if t.closed && Async.Channel.is_empty t.channel then
      None
    else
      Async.Channel.read_now t.channel

  let close t =
    t.closed <- true;
    Async.Channel.close t.channel

  let size t =
    Async.Channel.length t.channel
end
