open Core
open Async
open OUnit2

let test_post_office_routing _ctx =
  let po = Post_office.create () in
  
  let test_async () =
    let reader, writer = Pipe.create () in
    Post_office.start po;
    Post_office.register po ~name:"test_agent" ~writer;
    
    Post_office.route po ~target:"test_agent" "test message" >>= fun sent ->
    assert_bool "Message should be routed" sent;
    
    Pipe.read reader >>= function
    | `Ok msg -> 
        assert_equal "test message" msg;
        Post_office.stop po;
        return ()
    | `Eof -> 
        assert_failure "Should receive message"
  in
  
  Thread_safe.block_on_async_exn test_async

let test_post_office_unknown_route _ctx =
  let po = Post_office.create () in
  
  let test_async () =
    Post_office.start po;
    Post_office.route po ~target:"unknown" "test message" >>= fun sent ->
    assert_bool "Message should not be routed" (not sent);
    Post_office.stop po;
    return ()
  in
  
  Thread_safe.block_on_async_exn test_async

let suite =
  "post_office_tests" >::: [
    "test_routing" >:: test_post_office_routing;
    "test_unknown_route" >:: test_post_office_unknown_route;
  ]

let () = run_test_tt_main suite
