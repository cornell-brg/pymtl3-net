'''
==========================================================================
XbarMFlitRTL_test.py
==========================================================================
Test cases for the multi-flit xbar.

Author : Yanghui Ou
  Date : Feb 19, 2020
'''
import pytest
import hypothesis
from hypothesis import strategies as st
from pymtl3 import *
from pymtl3.stdlib.test import mk_test_case_table
from ocnlib.utils import to_bitstruct, run_sim
from ocnlib.packets import MultiFlitPacket as Packet
from ocnlib.test.test_srcs import MultiFlitPacketSourceRTL as TestSource
from ocnlib.test.test_sinks import MultiFlitPacketSinkRTL as TestSink
from ..XbarMFlitRTL import XbarMFlitRTL

#-------------------------------------------------------------------------
# TestHeader
#-------------------------------------------------------------------------

@bitstruct
class TestHeader:
  src    : Bits4
  dst    : Bits4
  opaque : Bits4
  plen   : Bits4

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, Header, num_inports, num_outports, pkts ):

    src_pkts, sink_pkts = \
      arrange_src_sink_pkts( Header, num_inports, num_outports, pkts )

    s.src  = [ TestSource( Header, src_pkts[i] ) for i in range( num_inports ) ]
    s.dut  = XbarMFlitRTL( Header, num_inports, num_outports )
    s.sink = [ TestSink( Header, sink_pkts[i] ) for i in range( num_outports ) ]

    for i in range( num_inports ):
      s.src[i].send //= s.dut.recv[i]

    for i in range( num_outports ):
      s.dut.send[i] //= s.sink[i].recv

  def done( s ):
    src_done = True
    sink_done = True
    for m in s.src:
      src_done &= m.done()
    for m in s.sink:
      sink_done &= m.done()
    return src_done and sink_done

  def line_trace( s ):
    return s.dut.line_trace()

#-------------------------------------------------------------------------
# mk_pkt
#-------------------------------------------------------------------------

def mk_pkt( src, dst, payload=[], opaque=0 ):
  plen        = len( payload )
  header      = TestHeader( src, dst, opaque, plen )
  header_bits = to_bits( header )
  flits       = [ header_bits ] + payload
  return Packet( TestHeader, flits )

#-------------------------------------------------------------------------
# arrange_src_sink_pkts
#-------------------------------------------------------------------------

def arrange_src_sink_pkts( Header, num_inports, num_outports, pkt_lst ):
  src_pkts  = [ [] for _ in range( num_inports  ) ]
  sink_pkts = [ [] for _ in range( num_outports ) ]

  for pkt in pkt_lst:
    header = to_bitstruct( pkt.flits[0], Header )
    src    = header.src.uint()
    dst    = header.dst.uint()
    src_pkts [ src ].append( pkt )
    sink_pkts[ dst ].append( pkt )

  return src_pkts, sink_pkts

#-------------------------------------------------------------------------
# test case: basic
#-------------------------------------------------------------------------

def basic_pkts( num_inports, num_outports ):
  return [
    #       src            dst             payload
    mk_pkt( 0,             0,              [                ] ),
    mk_pkt( 0,             num_outports-1, [                ] ),
    mk_pkt( num_inports-1, 0,              [ 0xface, 0xf00d ] ),
  ]

#-------------------------------------------------------------------------
# test case: neighbor
#-------------------------------------------------------------------------

def neighbor_pkts( num_inports, num_outports ):
  pkts = []
  for i in range( num_inports ):
    src = i
    dst = ( i+1 ) % num_outports
    plen = i % 10
    pkts.append( mk_pkt( src, dst, [ x+0xbad0 for x in range( plen ) ] ) )

  for i in range( num_inports ):
    src = i
    dst = ( i+1 ) % num_outports
    plen = ( i + 8 ) % 13
    pkts.append( mk_pkt( src, dst, [ x+0xace0 for x in range( plen ) ] ) )

  return pkts

#-------------------------------------------------------------------------
# test case: product
#-------------------------------------------------------------------------

def product_pkts( num_inports, num_outports ):
  pkts = []
  for i in range( num_inports ):
    for j in range( num_outports ):
      src = i
      dst = j
      plen = ( i + j ) % 16
      pkts.append( mk_pkt( src, dst, [ x+0xfee for x in range( plen ) ] ) )
      pkts.append( mk_pkt( src, dst, [ x+0xdad for x in range( plen ) ] ) )
  return pkts

#-------------------------------------------------------------------------
# test case table
#-------------------------------------------------------------------------

test_cases = [
  (                      'msg_func         n_in n_out init f_intv p_intv' ),
  [ 'basic2x2',           basic_pkts,      2,   2,    0,   0,     0       ],
  [ 'basic2x1',           basic_pkts,      2,   1,    0,   0,     0       ],
  [ 'basic2x9',           basic_pkts,      2,   9,    0,   0,     0       ],
  [ 'basic1x2',           basic_pkts,      1,   2,    0,   0,     0       ],
  [ 'neighbor4x4',        neighbor_pkts,   4,   4,    0,   0,     0       ],
  [ 'neighbor5x2',        neighbor_pkts,   5,   2,    0,   0,     0       ],
  [ 'neighbor3x3_delay',  neighbor_pkts,   4,   4,    5,   2,     9       ],
  [ 'product4x4',         product_pkts,    4,   4,    0,   0,     4       ],
  [ 'product8x8',         product_pkts,    8,   8,    0,   0,     2       ],
  [ 'product3x4',         product_pkts,    3,   4,    0,   0,     1       ],
  [ 'product7x3',         product_pkts,    7,   3,    0,   0,     1       ],
]

test_case_table = mk_test_case_table( test_cases )

#-------------------------------------------------------------------------
# test driver
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_mflit_xbar( test_params, test_verilog ):
  pkts = test_params.msg_func( test_params.n_in, test_params.n_out )
  trans_backend = 'yosys' if test_verilog else ''
  th = TestHarness( TestHeader, test_params.n_in, test_params.n_out, pkts )
  th.set_param( 'top.sink*.construct',
    initial_delay         = test_params.init,
    flit_interval_delay   = test_params.f_intv,
    packet_interval_delay = test_params.p_intv,
  )
  run_sim( th, translation=trans_backend )

#-------------------------------------------------------------------------
# packet strategy
#-------------------------------------------------------------------------

hex_words = [ 0xf00d, 0xfade, 0xface, 0xbeef, 0x8bad, 0xdeaf, 0xbabe ]

@st.composite
def pkt_strat( draw, num_inports, num_outports, max_plen=15 ):
  payload = draw( st.lists( st.sampled_from( hex_words ),
                            min_size=0, max_size=max_plen ) )
  src     = draw( st.integers(0, num_inports-1 ) )
  dst     = draw( st.integers(0, num_outports-1) )
  return mk_pkt( src, dst, payload )

#-------------------------------------------------------------------------
# pyh2 test
#-------------------------------------------------------------------------

@hypothesis.settings( deadline=None, max_examples=50 )
@hypothesis.given(
  num_inports  = st.integers(2, 16),
  num_outports = st.integers(1, 16),
  pkts         = st.data(),
)
def test_pyh2( num_inports, num_outports, pkts, test_verilog ):
  pkts = pkts.draw( st.lists( pkt_strat( num_inports, num_outports ), min_size=1, max_size=100 ) )
  trans_backend = 'yosys' if test_verilog else ''
  th = TestHarness( TestHeader, num_inports, num_outports, pkts )
  run_sim( th, translation=trans_backend )
