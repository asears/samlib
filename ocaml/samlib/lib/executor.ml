open Core
open Async

type task = unit -> unit Deferred.t

type t = {
  worker_count: int;
  tasks: task Pipe.Reader.t;
  task_writer: task Pipe.Writer.t;
  mutable running: bool;
}

let create ?(worker_count = 4) () =
  let reader, writer = Pipe.create () in
  { worker_count;
    tasks = reader;
    task_writer = writer;
    running = false }

let schedule t task =
  if t.running then
    Pipe.write t.task_writer task
  else
    return ()

let start t =
  t.running <- true;
  
  let rec worker () =
    if not t.running then
      return ()
    else
      Pipe.read t.tasks >>= function
      | `Eof -> return ()
      | `Ok task ->
          task () >>= fun () ->
          worker ()
  in
  
  let workers = 
    List.init t.worker_count ~f:(fun _ -> worker ()) in
  
  don't_wait_for (
    Deferred.all_unit workers >>| fun () ->
    t.running <- false
  )

let stop t =
  t.running <- false;
  Pipe.close t.task_writer
