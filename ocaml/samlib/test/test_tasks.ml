open Core
open Async
open OUnit2

let test_task_scheduling _ctx =
  let metrics = System_Metrics.create () in
  let scheduler = Scheduler.create ~metrics () in
  
  let test_async () =
    let task1_done = Scheduler.schedule scheduler ~id:"task1" (fun () ->
      return "task1 complete"
    ) in
    
    let task2_done = Scheduler.schedule scheduler ~priority:High (fun () ->
      return "task2 complete"
    ) ~id:"task2" in
    
    assert_equal 2 (Scheduler.task_count scheduler);
    
    Scheduler.run scheduler;
    
    Clock.after (Time.Span.of_sec 0.1) >>= fun () ->
    assert_bool "Task 1 should complete" !task1_done;
    assert_bool "Task 2 should complete" !task2_done;
    
    Scheduler.stop scheduler;
    return ()
  in
  
  Thread_safe.block_on_async_exn test_async

let test_task_metrics _ctx =
  let metrics = System_Metrics.create ~report_interval:(Time.Span.of_sec 0.1) () in
  let scheduler = Scheduler.create ~metrics () in
  
  let test_async () =
    let task_done = Scheduler.schedule scheduler ~id:"test_task" (fun () ->
      Clock.after (Time.Span.of_sec 0.05) >>= fun () ->
      return "done"
    ) in
    
    let reported = ref false in
    System_Metrics.start metrics ~on_report:(fun snapshot ->
      match Hashtbl.find snapshot "processing_time" with
      | Some (Metric.Histogram times) -> 
          assert_bool "Should have processing time" (List.length times > 0);
          reported := true;
          System_Metrics.stop metrics
      | _ -> ()
    );
    
    Scheduler.run scheduler;
    
    Clock.after (Time.Span.of_sec 0.2) >>= fun () ->
    assert_bool "Task should complete" !task_done;
    assert_bool "Metrics should be reported" !reported;
    
    Scheduler.stop scheduler;
    return ()
  in
  
  Thread_safe.block_on_async_exn test_async

let suite =
  "task_tests" >::: [
    "test_scheduling" >:: test_task_scheduling;
    "test_metrics" >:: test_task_metrics;
  ]

let () = run_test_tt_main suite
