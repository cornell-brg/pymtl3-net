'''
==========================================================================
adapters_test.py
==========================================================================
Unit tests for network adapters.

Author : Yanghui Ou
  Date : Apr 14, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.mem import mk_mem_msg, MemMsgType

from ..adapters import ReqAdapter, RespAdapter

#-------------------------------------------------------------------------
# constants
#-------------------------------------------------------------------------

Req, Resp = mk_mem_msg( 8, 32, 32 )
rd = MemMsgType.READ
wr = MemMsgType.WRITE

#-------------------------------------------------------------------------
# test case: req sanity check
#-------------------------------------------------------------------------

def test_req_sanity_check():
  dut = ReqAdapter( Req, Resp, id=0, num_requesters=4, num_responders=1,
                    max_req_in_flight=8 )
  dut.elaborate()
  dut.apply( DefaultPassGroup(linetrace=True) )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()

#-------------------------------------------------------------------------
# test case: resp sanity check
#-------------------------------------------------------------------------

def test_resp_sanity_check():
  dut = RespAdapter( Req, Resp, id=0, num_requesters=4, num_responders=1 )
  dut.elaborate()
  dut.apply( DefaultPassGroup(linetrace=True) )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()

#-------------------------------------------------------------------------
# test case: req adhoc
#-------------------------------------------------------------------------

def test_req_adhoc():
  dut = ReqAdapter( Req, Resp, id=2, num_requesters=16, num_responders=1,
                    max_req_in_flight=16 )
  print()
  dut.elaborate()
  dut.apply( DefaultPassGroup(linetrace=True) )

  dut.minion.respstream.rdy @= b1(1)
  dut.master.reqstream.rdy  @= b1(1)

  dut.sim_reset()

  assert dut.minion.reqstream.rdy
  assert dut.master.respstream.rdy

  dut.sim_eval_combinational()
  dut.print_line_trace()

  # cycle 3

  dut.sim_tick()
  assert dut.minion.reqstream.rdy
  assert dut.master.respstream.rdy

  dut.minion.reqstream.val @= b1(1)
  dut.minion.reqstream.msg @= Req( rd, 0xa0, 0x1000, 0, 0 )

  dut.sim_eval_combinational()
  dut.print_line_trace()

  assert dut.master.reqstream.val
  assert dut.master.reqstream.msg.payload.opaque[0:4] == 2
  assert dut.master.reqstream.msg.payload.opaque[4:8] == 15

  # cycle 4

  dut.sim_tick()
  assert dut.minion.reqstream.rdy
  assert dut.master.respstream.rdy

  dut.minion.reqstream.val @= b1(1)
  dut.minion.reqstream.msg @= Req( wr, 0xb0, 0x2000, 0, 0xfaceb00c )

  dut.sim_eval_combinational()
  dut.print_line_trace()

  # cycle 5

  dut.sim_tick()
  assert dut.minion.reqstream.rdy
  assert dut.master.respstream.rdy

  dut.minion.reqstream.val @= b1(1)
  dut.minion.reqstream.msg @= Req( rd, 0xc0, 0x3000, 0, 0 )

  dut.sim_eval_combinational()
  dut.print_line_trace()

  # cycle 6

  dut.sim_tick()
  assert dut.minion.reqstream.rdy
  assert dut.master.respstream.rdy

  dut.minion.reqstream.val  @= b1(0)

  dut.sim_eval_combinational()
  dut.print_line_trace()

  # cycle 7

  dut.sim_tick()
  assert dut.minion.reqstream.rdy
  assert dut.master.respstream.rdy

  dut.minion.reqstream.val  @= b1(0)

  dut.sim_eval_combinational()
  dut.print_line_trace()

  # cycle 8

  dut.sim_tick()
  assert dut.minion.reqstream.rdy
  assert dut.master.respstream.rdy

  dut.minion.reqstream.val  @= b1(0)
  dut.master.respstream.val @= b1(1)
  dut.master.respstream.msg.dst @= b4(2)
  dut.master.respstream.msg.payload @= Resp( wr, 0xe2, 0, 0, 0 )

  dut.sim_eval_combinational()
  dut.print_line_trace()

  assert dut.minion.respstream.val
  assert dut.minion.respstream.msg.opaque == 0xb0

  # cycle 9

  dut.sim_tick()
  assert dut.minion.reqstream.rdy
  assert dut.master.respstream.rdy

  dut.minion.reqstream.val  @= b1(0)
  dut.master.respstream.val @= b1(0)

  dut.sim_eval_combinational()
  dut.print_line_trace()

#-------------------------------------------------------------------------
# test case: resp adhoc
#-------------------------------------------------------------------------

def test_resp_adhoc():
  dut = RespAdapter( Req, Resp, id=0, num_requesters=16, num_responders=1 )
  print()
  dut.elaborate()
  dut.apply( DefaultPassGroup(linetrace=True) )

  dut.minion.respstream.rdy @= b1(1)
  dut.master.reqstream.rdy  @= b1(1)

  dut.sim_reset()

  assert dut.minion.reqstream.rdy
  assert dut.master.respstream.rdy

  dut.sim_eval_combinational()
  dut.print_line_trace()

  # cycle 3

  dut.sim_tick()
  assert dut.minion.reqstream.rdy
  assert dut.master.respstream.rdy

  dut.minion.reqstream.val @= b1(1)
  dut.minion.reqstream.msg.dst @= b1(0)
  dut.minion.reqstream.msg.payload @= Req( rd, 0xf2, 0x1000, 0, 0 )

  dut.sim_eval_combinational()
  dut.print_line_trace()

  assert dut.master.reqstream.val
  assert dut.master.reqstream.msg == Req( rd, 0xf2, 0x1000, 0, 0 )

  # cycle 4

  dut.sim_tick()
  assert dut.minion.reqstream.rdy
  assert dut.master.respstream.rdy

  dut.minion.reqstream.val  @= b1(0)
  dut.master.respstream.val @= b1(1)
  dut.master.respstream.msg @= Resp( rd, 0xf2, 0, 0, 0xfaceb00c )

  dut.sim_eval_combinational()
  dut.print_line_trace()

  assert dut.minion.respstream.val
  assert dut.minion.respstream.msg.dst == 2
  assert dut.minion.respstream.msg.payload == Resp( rd, 0xf2, 0, 0, 0xfaceb00c )

  # cycle 5

  dut.sim_tick()
  assert dut.minion.reqstream.rdy
  assert dut.master.respstream.rdy

  dut.minion.reqstream.val @= b1(0)
  dut.master.respstream.val @= b1(0)

  dut.sim_eval_combinational()
  dut.print_line_trace()
