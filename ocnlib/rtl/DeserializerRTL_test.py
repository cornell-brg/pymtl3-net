'''
==========================================================================
DeserializerRTL_test.py
==========================================================================
Unit tests for DeserializerRTL.

Author : Yanghui Ou
  Date : Feb 26, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.test.test_srcs import TestSrcRTL as TestSource
from pymtl3.stdlib.test.test_sinks import TestSinkRTL as TestSink
from ocnlib.utils import run_sim

from .DeserializerRTL import DeserializerRTL

#-------------------------------------------------------------------------
# mk_msgs
#-------------------------------------------------------------------------

def mk_msgs( in_nbits, max_nblocks, msgs ):
  InType    = mk_bits( in_nbits )
  OutType   = mk_bits( in_nbits * max_nblocks )
  LenType   = mk_bits( clog2( max_nblocks+1 ) )
  sink_msgs = [ InType(x) for x in msgs[::2] ]
  len_lst   = [ LenType(x) for x in msgs[1::2] ]

  src_msgs = []
  for data, length in zip( sink_msgs, len_lst ):
    assert length.uint() > 0
    for i in range( length.uint() ):
      src_msgs.append( data[i:out_nbits:(i+1)*out_nbits] )

  # 0-padding len_msgs
  len_msgs = []
  for x in len_lst:
    for _ in range( x ):
      len_msgs.append( x )

  return src_msgs, len_msgs, sink_msgs

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):
  def construct( s, in_nbits, max_nblocks, msgs ):
    InType    = mk_bits( in_nbits )
    OutType   = mk_bits( in_nbits * max_nblocks )
    LenType   = mk_bits( clog2( max_nblocks+1 ) )
    src_msgs, len_msgs, sink_msgs = mk_msgs( in_nbits, max_nblocks, msgs )

    s.src     = TestSource( InType, src_msgs  )
    s.src_len = TestSource( LenType, len_msgs )
    s.dut     = DeserializerRTL( in_nbits, max_nblocks )
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
  dut = DeserializerRTL( in_nbits=16, max_nblocks=4 )
  dut.elaborate()
  dut.apply( SimulationPass() )
  dut.sim_reset()
  dut.tick()
  dut.tick()

  th = TestHarness( 16, 8, [] )
  th.elaborate()
  th.apply( SimulationPass() )
  th.tick()
  th.tick()