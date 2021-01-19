'''
==========================================================================
DeserializerRTL_test.py
==========================================================================
Unit tests for DeserializerRTL.

Author : Yanghui Ou
  Date : Feb 26, 2020
'''
import os
import hypothesis
from hypothesis import strategies as st
from pymtl3 import *
from pymtl3.datatypes.strategies import bits
from pymtl3.stdlib.test_utils.test_srcs import TestSrcRTL as TestSource
from pymtl3.stdlib.test_utils.test_sinks import TestSinkRTL as TestSink

from ocnlib.utils import run_sim

from .DeserializerRTL import DeserializerRTL

#-------------------------------------------------------------------------
# mk_msgs
#-------------------------------------------------------------------------

def mk_msgs( in_nbits, max_nblocks, msgs ):
  InType    = mk_bits( in_nbits )
  OutType   = mk_bits( in_nbits * max_nblocks )
  LenType   = mk_bits( clog2( max_nblocks+1 ) )
  sink_msgs = [ OutType(x) for x in msgs[::2] ]
  len_lst   = [ LenType(x) for x in msgs[1::2] ]

  sink_msgs = [ zext(data[0:in_nbits*length.uint()], OutType) for data, length in zip( sink_msgs, len_lst ) ]

  src_msgs = []
  for data, length in zip( sink_msgs, len_lst ):
    assert length.uint() > 0
    for i in range( length.uint() ):
      src_msgs.append( data[i*in_nbits:(i+1)*in_nbits] )

  # pad len_msgs
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
  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()

  th = TestHarness( 16, 8, [] )
  th.elaborate()
  th.apply( DefaultPassGroup() )
  th.sim_tick()
  th.sim_tick()

#-------------------------------------------------------------------------
# test case: basic
#-------------------------------------------------------------------------

def test_basic( cmdline_opts ):
  msgs = [
    0xfaceb00c,         2,
    0xdeadbeef,         1,
    0xcafebabefa11deaf, 4,
    0xace3ace2ace1ace0, 3,
  ]
  th = TestHarness( 16, 4, msgs )
  run_sim( th, cmdline_opts, max_cycles=20 )

#-------------------------------------------------------------------------
# test case: backpressure
#-------------------------------------------------------------------------

def test_backpressure( cmdline_opts ):
  msgs = [
    0xfaceb00c,         2,
    0xdeadbeef,         1,
    0xcafebabefa11deaf, 4,
    0xace3ace2ace1ace0, 3,
  ]
  th = TestHarness( 16, 4, msgs )
  th.set_param( 'top.sink.construct', initial_delay=10, interval_delay=2 )
  run_sim( th, cmdline_opts, max_cycles=40 )

#-------------------------------------------------------------------------
# test case: src delay
#-------------------------------------------------------------------------

def test_src_delay( cmdline_opts ):
  msgs = [
    0xdeadbeef_faceb00c,                   2,
    0xbad0bad0_deadbeef,                   1,
    0xcafebabe_fa11deaf_deadc0de_faceb00c, 4,
    0xace5ace4_ace3ace2_ace1ace0,          3,
  ]
  th = TestHarness( 32, 9, msgs )
  th.set_param( 'top.src*.construct', initial_delay=10, interval_delay=2 )
  run_sim( th, cmdline_opts, max_cycles=200 )

#-------------------------------------------------------------------------
# test case: stream
#-------------------------------------------------------------------------

def test_stream( cmdline_opts ):
  msgs = [
    0xdeadbeef, 1,
    0xbad0bad0, 1,
    0xcafebabe, 1,
    0xace5ace4, 1,
    0xfaceb00c_ace5ace4, 2,
    0x8badf00d_ace5ace4, 2,
    0x8badc0de_ace5ace4, 2,
    0xfeedbabe_ace5ace4, 2,
  ]
  th = TestHarness( 32, 4, msgs )
  run_sim( th, cmdline_opts, max_cycles=40 )

#-------------------------------------------------------------------------
# test case: pyh2
#-------------------------------------------------------------------------

@hypothesis.settings( deadline=None, max_examples=100 if 'CI' not in os.environ else 5 )
@hypothesis.given(
  in_nbits    = st.integers(1, 64),
  max_nblocks = st.integers(2, 15),
  data        = st.data(),
)
def test_pyh2( in_nbits, max_nblocks, data, cmdline_opts ):
  len_msgs = data.draw( st.lists( st.integers(1, max_nblocks), min_size=1, max_size=100 ) )
  src_msgs = [ data.draw( st.integers(0, 2**(x*in_nbits)-1) ) for x in len_msgs ]

  msgs = []
  for x, l in zip( src_msgs, len_msgs ):
    msgs.append( x )
    msgs.append( l )

  th = TestHarness( in_nbits, max_nblocks, msgs )
  run_sim( th, cmdline_opts )
