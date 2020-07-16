"""
==========================================================================
 CreditIfc_test.py
==========================================================================
Test for credit based interfaces.

Author : Yanghui Ou
  Date : June 10, 2019
"""
from pymtl3 import *
from pymtl3.stdlib.queues import NormalQueueRTL
from pymtl3.stdlib.test_utils.test_sinks import TestSinkRTL
from pymtl3.stdlib.test_utils.test_srcs import TestSrcRTL

from ocnlib.utils import run_sim
from ocnlib.test.net_sinks import TestNetSinkRTL

from .CreditIfc import (CreditRecvIfcRTL, CreditRecvRTL2SendRTL,
                        CreditSendIfcRTL, RecvRTL2CreditSendRTL)
from .packets import mk_generic_pkt

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):
  def construct( s, Type, src_msgs, sink_msgs, credit_line=2 ):

    s.src = TestSrcRTL( Type, src_msgs )
    s.src_adapter = RecvRTL2CreditSendRTL( Type, vc=2, credit_line=credit_line )
    s.sink_adapter = CreditRecvRTL2SendRTL( Type, vc=2, credit_line=credit_line, QType=NormalQueueRTL )
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

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

def test_simple():
  Pkt = mk_generic_pkt( vc=2, payload_nbits=32 )
  msgs = [
    Pkt( 0, 1, 0x04, 0, 0xdeadbabe ),
    Pkt( 0, 2, 0x02, 1, 0xfaceb00c ),
    Pkt( 0, 3, 0x03, 0, 0xdeadface ),
  ]
  th = TestHarness( Pkt, msgs, msgs )
  run_sim( th )

def test_backpresure():
  Pkt = mk_generic_pkt( vc=2, payload_nbits=32 )
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
  run_sim( th )
