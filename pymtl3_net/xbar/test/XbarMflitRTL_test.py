'''
==========================================================================
XbarMflitRTL_test.py
==========================================================================
Test cases for the multi-flit xbar.

Author : Yanghui Ou
  Date : Feb 19, 2020
'''
import os
import pytest
import hypothesis
from hypothesis import strategies as st
from pymtl3 import *
from pymtl3.stdlib.test_utils import mk_test_case_table
from pymtl3_net.ocnlib.utils import run_sim
from pymtl3_net.ocnlib.packets import MflitPacket as Packet
from pymtl3_net.ocnlib.test.test_srcs import MflitPacketSourceRTL as TestSource
from pymtl3_net.ocnlib.test.test_sinks import MflitPacketSinkRTL as TestSink
from ..XbarMflitRTL import XbarMflitRTL

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
    s.dut  = XbarMflitRTL( Header, num_inports, num_outports )
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
  header_bits = header.to_bits()
  flits       = [ header_bits ] + payload
  return Packet( TestHeader, flits )

#-------------------------------------------------------------------------
# arrange_src_sink_pkts
#-------------------------------------------------------------------------

def arrange_src_sink_pkts( Header, num_inports, num_outports, pkt_lst ):
  src_pkts  = [ [] for _ in range( num_inports  ) ]
  sink_pkts = [ [] for _ in range( num_outports ) ]

  for pkt in pkt_lst:
    header = Header.from_bits( pkt.flits[0] )
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
# test case: hotspot
#-------------------------------------------------------------------------

def hotspot_pkts( num_inports, num_outports ):
  pkts  = []
  npkts = 10
  for i in range( num_inports ):
    for j in range( npkts ):
      pkts.append( mk_pkt( i, num_outports-1, [ 0xbad0+i, 0xace0+j ] ) )
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
  [ 'product8x1',         product_pkts,    8,   1,    0,   0,     0       ],
  [ 'product8x1_delay',   product_pkts,    8,   1,    0,   0,     10      ],
  [ 'product8x1_delay',   product_pkts,    8,   1,    0,   0,     10      ],
  [ 'hotspot4x1',         hotspot_pkts,    4,   1,    0,   0,     0       ],
  [ 'hotspot4x1_delay',   hotspot_pkts,    4,   1,    0,   0,     13      ],
]

test_case_table = mk_test_case_table( test_cases )

#-------------------------------------------------------------------------
# test driver
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_mflit_xbar( test_params, cmdline_opts ):
  pkts = test_params.msg_func( test_params.n_in, test_params.n_out )
  th   = TestHarness( TestHeader, test_params.n_in, test_params.n_out, pkts )
  th.set_param( 'top.sink*.construct',
    initial_delay         = test_params.init,
    flit_interval_delay   = test_params.f_intv,
    packet_interval_delay = test_params.p_intv,
  )
  run_sim( th, cmdline_opts )

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

# FIXME: figure out a way to work around the health check
@hypothesis.settings(
  deadline=None,
  max_examples=50 if 'CI' not in os.environ else 5,
  suppress_health_check=[ hypothesis.HealthCheck.function_scoped_fixture ],
)
@hypothesis.given(
  num_inports  = st.integers(1, 16),
  num_outports = st.integers(1, 16),
  pkts         = st.data(),
)
def test_pyh2( num_inports, num_outports, pkts, cmdline_opts ):
  pkts = pkts.draw( st.lists( pkt_strat( num_inports, num_outports ), min_size=1, max_size=100 ) )
  th = TestHarness( TestHeader, num_inports, num_outports, pkts )
  run_sim( th, cmdline_opts )
