'''
==========================================================================
SerializerRTL_test.py
==========================================================================
Unit tests for SerializerRTL.

Author : Yanghui Ou
  Date : Feb 26, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.test.test_srcs import TestSrcRTL as TestSource
from pymtl3.stdlib.test.test_sinks import TestSinkRTL as TestSink

from .SerializerRTL import SerializerRTL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):
  def construct( s, out_nbits, max_nblocks, src_msgs, len_msgs, sink_msgs ):
    InType  = mk_bits( out_nbits*( max_nblocks ) )
    OutType = mk_bits( out_nbits )
    LenType =  mk_bits( clog2( max_nblocks+1 ) )

    s.src     = TestSource( InType, src_msgs )
    s.src_len = TestSource( LenType, len_msgs )
    s.dut     = SerializerRTL( out_nbits, max_nblocks )
    s.sink    = TestSink( OutType, sink_msgs )

    connect( s.src.send,         s.dut.recv     )
    connect( s.src_len.send.rdy, s.dut.recv.rdy )
    connect( s.src_len.send.msg, s.dut.len      )
    connect( s.dut.send,         s.sink.recv    )

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return s.dut.line_trace()

#-------------------------------------------------------------------------
# test case: sanity check
#-------------------------------------------------------------------------

def test_sanity_check():
  dut = SerializerRTL( out_nbits=16, max_nblocks=4 )
  dut.elaborate()
  dut.apply( SimulationPass() )
  dut.sim_reset()
  dut.tick()
  dut.tick()

  th = TestHarness( 16, 8, [], [], [] )
  th.elaborate()
  th.apply( SimulationPass() )
  th.tick()
  th.tick()
