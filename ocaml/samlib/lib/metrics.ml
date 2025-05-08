open Core
open Async

module Metric = struct
  type t =
    | Counter of int
    | Gauge of float
    | Histogram of float list
  [@@deriving sexp, show]

  let update = function
    | Counter n -> Counter (n + 1)
    | Gauge v -> Gauge v
    | Histogram vs -> Histogram vs
end

module Reporter = struct
  type t = {
    metrics: (string, Metric.t) Hashtbl.t;
    mutable running: bool;
    report_interval: Time.Span.t;
  }

  let create ?(report_interval = Time.Span.of_sec 60.0) () = {
    metrics = Hashtbl.create (module String);
    running = false;
    report_interval;
  }

  let record t ~name ~value =
    Hashtbl.set t.metrics ~key:name ~data:value

  let increment_counter t ~name =
    match Hashtbl.find t.metrics name with
    | Some (Counter n) -> Hashtbl.set t.metrics ~key:name ~data:(Counter (n + 1))
    | _ -> Hashtbl.set t.metrics ~key:name ~data:(Counter 1)

  let update_gauge t ~name ~value =
    Hashtbl.set t.metrics ~key:name ~data:(Gauge value)

  let add_to_histogram t ~name ~value =
    match Hashtbl.find t.metrics name with
    | Some (Histogram vs) -> 
        Hashtbl.set t.metrics ~key:name ~data:(Histogram (value :: vs))
    | _ -> 
        Hashtbl.set t.metrics ~key:name ~data:(Histogram [value])

  let start t ~on_report =
    t.running <- true;
    
    let rec report_loop () =
      if not t.running then
        return ()
      else
        Clock.after t.report_interval >>= fun () ->
        let snapshot = Hashtbl.copy t.metrics in
        don't_wait_for (on_report snapshot);
        report_loop ()
    in
    
    don't_wait_for (report_loop ())

  let stop t =
    t.running <- false
end

module System_Metrics = struct
  type t = {
    reporter: Reporter.t;
    start_time: Time.t;
  }

  let create ?(report_interval = Time.Span.of_sec 60.0) () =
    let reporter = Reporter.create ~report_interval () in
    { reporter; start_time = Time.now () }

  let record_message_sent t =
    Reporter.increment_counter t.reporter ~name:"messages_sent"

  let record_message_received t =
    Reporter.increment_counter t.reporter ~name:"messages_received"

  let record_agent_count t count =
    Reporter.update_gauge t.reporter ~name:"active_agents" ~value:(Float.of_int count)

  let record_processing_time t duration =
    Reporter.add_to_histogram t.reporter ~name:"processing_time" ~value:duration

  let start t ~on_report =
    Reporter.start t.reporter ~on_report

  let stop t =
    Reporter.stop t.reporter

  let uptime t =
    Time.diff (Time.now ()) t.start_time
end
