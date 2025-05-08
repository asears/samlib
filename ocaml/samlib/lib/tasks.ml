open Core
open Async

type task_priority = High | Normal | Low
[@@deriving sexp, show, eq, compare]

type 'a task = {
  id: string;
  priority: task_priority;
  work: unit -> 'a Deferred.t;
  created_at: Time.t;
}

module Scheduler = struct
  type 'a t = {
    tasks: ('a task * bool ref) Queue.t;
    mutable running: bool;
    metrics: System_Metrics.t;
  }

  let create ~metrics () = {
    tasks = Queue.create ();
    running = false;
    metrics;
  }

  let schedule t ?(priority = Normal) ~id work =
    let task = {
      id;
      priority;
      work;
      created_at = Time.now ();
    } in
    let completed = ref false in
    Queue.enqueue t.tasks (task, completed);
    completed

  let run t =
    t.running <- true;
    
    let rec process_next () =
      if not t.running then
        return ()
      else
        match Queue.dequeue t.tasks with
        | None -> 
            Clock.after (Time.Span.of_millisecond 1.0) >>= fun () ->
            process_next ()
        | Some (task, completed) ->
            let start_time = Time.now () in
            task.work () >>= fun _ ->
            completed := true;
            let duration = Time.diff (Time.now ()) start_time |> Time.Span.to_sec in
            System_Metrics.record_processing_time t.metrics duration;
            process_next ()
    in
    
    don't_wait_for (process_next ())

  let stop t =
    t.running <- false

  let task_count t =
    Queue.length t.tasks
end
