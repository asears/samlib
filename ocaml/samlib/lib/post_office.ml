open Core
open Async

(** Message routing and delivery service *)
type t = {
  routes: (string, string Pipe.Writer.t) Hashtbl.t;
  mutable running: bool;
}

let create () = {
  routes = Hashtbl.create (module String);
  running = false;
}

let register t ~name ~writer =
  if t.running then
    Hashtbl.set t.routes ~key:name ~data:writer

let unregister t ~name =
  if t.running then
    Hashtbl.remove t.routes name

let route t ~target msg =
  match Hashtbl.find t.routes target with
  | Some writer -> 
      Pipe.write writer msg >>| fun () -> true
  | None -> 
      return false

let start t =
  t.running <- true

let stop t =
  t.running <- false;
  Hashtbl.iter t.routes ~f:Pipe.close_write
