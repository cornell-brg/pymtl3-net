"""
==========================================================================
 SwitchUnitCL_test.py
==========================================================================

Author: Yanghui Ou
  Date: July 2, 2019
"""
import pytest
from pymtl3 import *
from pymtl3.stdlib.test.test_srcs import TestSrcCL
from pymtl3.stdlib.cl.queues import BypassQueueCL
from ocn_pclib.test.net_sinks import TestNetSinkCL as TestSinkCL

from router.SwitchUnitCL import SwitchUnitCL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, MsgType, src_msgs, sink_msgs, num_inports=5 ):

    match_func = lambda a,b : a==b
    s.src   = [ TestSrcCL( MsgType, src_msgs[i] ) for i in range(num_inports) ]
    s.src_q = [ BypassQueueCL( num_entries=1 ) for _ in range(num_inports) ]
    s.dut   = SwitchUnitCL( MsgType, num_inports )
    s.sink  = TestSinkCL( MsgType, sink_msgs, match_func=match_func )

    # Connections
    for i in range( 5 ):
      s.connect( s.src[i].send,  s.src_q[i].enq )
      s.connect( s.src_q[i].deq, s.dut.get[i]   )

    @s.update
    def up_give_recv():
      if s.dut.give.rdy() and s.sink.recv.rdy():
        s.sink.recv( s.dut.give() )

  def done( s ):
    srcs_done = True
    for i in range( 5 ):
      if not s.src[i].done():
        srcs_done = False
    return srcs_done and s.sink.done()

  def line_trace( s ):
    return "{}".format( s.dut.line_trace() )

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

class SwitchUnitCL_Tests( object ):

  @classmethod
  def setup_class( cls ):
    cls.TestHarness = TestHarness

  def run_sim( s, th, max_cycles=100 ):

    # Create a simulator
    th.apply( DynamicSim )
    th.sim_reset()

    # Run simulation

    ncycles = 0
    print ""
    print "{:3}:{}".format( ncycles, th.line_trace() )
    while not th.done() and ncycles < max_cycles:
      th.tick()
      ncycles += 1
      print "{:3}:{}".format( ncycles, th.line_trace() )

    # Check timeout
    assert ncycles < max_cycles

  def test_su5_simple( s ):
    src_msgs    = [ [] for _ in range(5) ]
    src_msgs[0] = [ b16(4), b16(5)  ]
    src_msgs[1] = [ b16(2), b16(8)  ]
    src_msgs[2] = [ b16(4), b16(13) ]
    src_msgs[3] = [ b16(6), b16(18) ]
    src_msgs[4] = [ b16(8), b16(23) ]
    sink_msg = [ msg for i in range(5) for msg in src_msgs[i]  ]
    th = s.TestHarness( Bits16, src_msgs, sink_msg, num_inports=5 )
    s.run_sim( th )