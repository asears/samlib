open Core
open Async
open OUnit2

(* Test message module *)
module Test_Message = struct
  type t = string [@@deriving sexp, show, eq]
end

module Test_Channel = Channel.Make(Test_Message)

let test_channel_send_receive _ctx =
  let channel = Test_Channel.create () in
  
  let test_async () =
    Test_Channel.send channel "test message" >>= fun sent ->
    assert_bool "Message should be sent" sent;
    
    Test_Channel.receive channel >>= function
    | Some msg -> 
        assert_equal ~printer:Test_Message.show "test message" msg;
        return ()
    | None -> 
        assert_failure "Should receive message"
  in
  
  Thread_safe.block_on_async_exn test_async

let test_channel_close _ctx =
  let channel = Test_Channel.create () in
  
  let test_async () =
    Test_Channel.close channel;
    Test_Channel.send channel "test message" >>= fun sent ->
    assert_bool "Message should not be sent to closed channel" (not sent);
    return ()
  in
  
  Thread_safe.block_on_async_exn test_async

let suite =
  "channel_tests" >::: [
    "test_send_receive" >:: test_channel_send_receive;
    "test_close" >:: test_channel_close;
  ]

let () = run_test_tt_main suite
