open Core
open Async
open OUnit2

let test_metrics_counter _ctx =
  let reporter = Reporter.create ~report_interval:(Time.Span.of_sec 0.1) () in
  
  let test_async () =
    Reporter.increment_counter reporter ~name:"test_counter";
    Reporter.increment_counter reporter ~name:"test_counter";
    
    let reported = ref false in
    Reporter.start reporter ~on_report:(fun snapshot ->
      match Hashtbl.find snapshot "test_counter" with
      | Some (Metric.Counter n) -> 
          assert_equal 2 n;
          reported := true;
          Reporter.stop reporter
      | _ -> assert_failure "Expected counter metric"
    );
    
    Clock.after (Time.Span.of_sec 0.2) >>= fun () ->
    assert_bool "Metric should be reported" !reported;
    return ()
  in
  
  Thread_safe.block_on_async_exn test_async

let test_system_metrics _ctx =
  let metrics = System_Metrics.create ~report_interval:(Time.Span.of_sec 0.1) () in
  
  let test_async () =
    System_Metrics.record_message_sent metrics;
    System_Metrics.record_message_received metrics;
    System_Metrics.record_agent_count metrics 5;
    System_Metrics.record_processing_time metrics 0.1;
    
    let reported = ref false in
    System_Metrics.start metrics ~on_report:(fun snapshot ->
      assert_bool "Should have messages_sent" (Hashtbl.mem snapshot "messages_sent");
      assert_bool "Should have active_agents" (Hashtbl.mem snapshot "active_agents");
      reported := true;
      System_Metrics.stop metrics
    );
    
    Clock.after (Time.Span.of_sec 0.2) >>= fun () ->
    assert_bool "Metrics should be reported" !reported;
    return ()
  in
  
  Thread_safe.block_on_async_exn test_async

let suite =
  "metrics_tests" >::: [
    "test_counter" >:: test_metrics_counter;
    "test_system_metrics" >:: test_system_metrics;
  ]

let () = run_test_tt_main suite
