"""
==========================================================================
 CreditIfc_test.py
==========================================================================
Test for credit based interfaces.

Author : Yanghui Ou
  Date : June 10, 2019
"""
from pymtl3 import *
from pymtl3.passes.PassGroups import DynamicSim
from pymtl3.stdlib.test.test_srcs import TestSrcRTL
from pymtl3.stdlib.test.test_sinks import TestSinkRTL
from pymtl3.stdlib.rtl.queues import NormalQueueRTL

from ocn_pclib.test.net_sinks import TestNetSinkRTL
from .packets import mk_generic_pkt
from .CreditIfc import(
  CreditRecvIfcRTL,
  CreditSendIfcRTL,
  RecvRTL2CreditSendRTL,
  CreditRecvRTL2SendRTL,
)

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):
  def construct( s, Type, src_msgs, sink_msgs, credit_line=2 ):

    s.src = TestSrcRTL( Type, src_msgs )
    s.src_adapter = RecvRTL2CreditSendRTL( Type, nvcs=2, credit_line=credit_line )
    s.sink_adapter = CreditRecvRTL2SendRTL( Type, nvcs=2, credit_line=credit_line, QType=NormalQueueRTL )
    s.sink = TestNetSinkRTL( Type, sink_msgs )

    s.src.send          //= s.src_adapter.recv
    s.src_adapter.send  //= s.sink_adapter.recv
    s.sink_adapter.send //= s.sink.recv

  def line_trace( s ):
    return "{} > {} > {} > {}".format(
      s.src.line_trace(),
      s.src_adapter.line_trace(),
      s.sink_adapter.line_trace(),
      s.sink.line_trace()
    )

  def done( s ):
    return s.src.done() and s.sink.done()

  def run_sim( s, max_cycles=50 ):
    # Run simulation
    print()
    ncycles = 0
    s.sim_reset()
    print("{:3}: {}".format( ncycles, s.line_trace() ))
    while not s.done() and ncycles < max_cycles:
      s.tick()
      ncycles += 1
      print("{:3}: {}".format( ncycles, s.line_trace() ))

    # Check timeout
    assert ncycles < max_cycles

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

def test_simple():
  Pkt = mk_generic_pkt( nvcs=2 )
  msgs = [
    Pkt( 0, 1, 0x04, 0, 0xdeadbabe ),
    Pkt( 0, 2, 0x02, 1, 0xfaceb00c ),
    Pkt( 0, 3, 0x03, 0, 0xdeadface ),
  ]
  th = TestHarness( Pkt, msgs, msgs )
  th.apply( SimpleSim )
  th.sim_reset()
  th.run_sim()

def test_backpresure():
  Pkt = mk_generic_pkt( nvcs=2 )
  msgs = [
     # src dst opq vc_id  payload
    Pkt( 0, 1, 0x04, 0, 0xdeadbabe ),
    Pkt( 0, 2, 0x02, 1, 0xfaceb00c ),
    Pkt( 0, 3, 0x03, 0, 0xdeadface ),
    Pkt( 0, 3, 0x03, 1, 0xdeadface ),
    Pkt( 0, 3, 0x03, 1, 0xdeadface ),
    Pkt( 0, 3, 0x03, 0, 0xdeadface ),
    Pkt( 0, 3, 0x03, 0, 0xdeadface ),
  ]
  th = TestHarness( Pkt, msgs, msgs )
  th.set_param( "top.sink.construct", initial_delay=20)
  th.apply( SimpleSim )
  th.sim_reset()
  th.run_sim()
