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
from ocnlib.utils import run_sim
# from pymtl3.stdlib.test import run_sim

from .SerializerRTL import SerializerRTL

#-------------------------------------------------------------------------
# mk_msgs
#-------------------------------------------------------------------------

def mk_msgs( out_nbits, max_nblocks, msgs ):
  InType    = mk_bits( out_nbits*( max_nblocks ) )
  OutType   = mk_bits( out_nbits )
  LenType   = mk_bits( clog2( max_nblocks+1 ) )
  src_msgs  = [ InType(x) for x in msgs[::2] ]
  len_msgs  = [ LenType(x) for x in msgs[1::2] ]

  sink_msgs = []
  for data, length in zip( src_msgs, len_msgs ):
    assert length.uint() > 0
    for i in range( length.uint() ):
      sink_msgs.append( data[i*out_nbits:(i+1)*out_nbits] )

  return src_msgs, len_msgs, sink_msgs

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):
  def construct( s, out_nbits, max_nblocks, msgs ):
    InType  = mk_bits( out_nbits*( max_nblocks ) )
    OutType = mk_bits( out_nbits )
    LenType =  mk_bits( clog2( max_nblocks+1 ) )
    src_msgs, len_msgs, sink_msgs = mk_msgs( out_nbits, max_nblocks, msgs )
    print( sink_msgs )

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

  th = TestHarness( 16, 8, [] )
  th.elaborate()
  th.apply( SimulationPass() )
  th.tick()
  th.tick()

#-------------------------------------------------------------------------
# test case: basic
#-------------------------------------------------------------------------

def test_basic():
  msgs = [
    0xfaceb00c,         2,
    0xdeadbeef,         1,
    0xcafebabefa11deaf, 4,
    0xace3ace2ace1ace0, 3,
  ]
  th = TestHarness( 16, 4, msgs )
  run_sim( th, max_cycles=20 )

#-------------------------------------------------------------------------
# test case: backpressure
#-------------------------------------------------------------------------

def test_backpressure():
  msgs = [
    0xfaceb00c,         2,
    0xdeadbeef,         1,
    0xcafebabefa11deaf, 4,
    0xace3ace2ace1ace0, 3,
  ]
  th = TestHarness( 16, 4, msgs )
  th.set_param( 'top.sink.construct', initial_delay=10, interval_delay=2 )
  run_sim( th, max_cycles=40 )

