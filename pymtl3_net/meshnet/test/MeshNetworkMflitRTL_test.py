'''
==========================================================================
MeshNetworkMflitRTL_test.py
==========================================================================
Test cases for multi-flit mesh.

Author : Yanghui Ou
  Date : Feb 14, 2020
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
from ..MeshNetworkMflitRTL import MeshNetworkMflitRTL

#-------------------------------------------------------------------------
# TestHeader
#-------------------------------------------------------------------------

@bitstruct
class TestHeader:
  opaque: Bits8
  src_x : Bits4
  src_y : Bits4
  dst_x : Bits4
  dst_y : Bits4
  plen  : Bits8

#-------------------------------------------------------------------------
# TestPosition
#-------------------------------------------------------------------------

@bitstruct
class TestPosition:
  pos_x : Bits4
  pos_y : Bits4

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, Header, Position, ncols, nrows, src_pkts, sink_pkts ):
    nterminals = ncols * nrows

    s.src  = [ TestSource( Header, src_pkts[i] ) for i in range( nterminals ) ]
    s.dut  = MeshNetworkMflitRTL( Header, Position, ncols, nrows )
    s.sink = [ TestSink( Header, sink_pkts[i] ) for i in range( nterminals ) ]

    for i in range( nterminals ):
      s.src[i].send //= s.dut.recv[i]
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

def mk_pkt( src_x, src_y, dst_x, dst_y, payload=[], opaque=0 ):
  plen        = len( payload )
  header      = TestHeader( opaque, src_x, src_y, dst_x, dst_y, plen )
  header_bits = header.to_bits()
  flits       = [ header_bits ] + payload
  return Packet( TestHeader, flits )

#-------------------------------------------------------------------------
# arrange_src_sink_pkts
#-------------------------------------------------------------------------

def arrange_src_sink_pkts( Header, ncols, nrows, pkt_lst ):
  nterminals = ncols * nrows
  src_pkts  = [ [] for _ in range( nterminals ) ]
  sink_pkts = [ [] for _ in range( nterminals ) ]

  for pkt in pkt_lst:
    header = Header.from_bits( pkt.flits[0] )
    src_id = header.src_x.uint() + header.src_y.uint() * ncols
    dst_id = header.dst_x.uint() + header.dst_y.uint() * ncols
    src_pkts [ src_id ].append( pkt )
    sink_pkts[ dst_id ].append( pkt )

  return src_pkts, sink_pkts

#-------------------------------------------------------------------------
# sanity check
#-------------------------------------------------------------------------

def test_sanity_check():
  net = MeshNetworkMflitRTL( TestHeader, TestPosition, ncols=2, nrows=2 )
  net.elaborate()
  net.apply( DefaultPassGroup() )
  net.sim_reset()
  net.sim_tick()

#-------------------------------------------------------------------------
# test case: basic
#-------------------------------------------------------------------------

def basic_pkts( ncols, nrows ):
  return [
    #       src_x    y        dst_x    y        payload
    mk_pkt(     0,   0,       ncols-1, nrows-1, [ 0x8badf00d             ] ),
    mk_pkt( ncols-1, nrows-1, 0,       0,       [ 0x8badbabe, 0xdeadbeef ] ),
  ]

#-------------------------------------------------------------------------
# test case: basic
#-------------------------------------------------------------------------

def neighbor_pkts( ncols, nrows ):
  pkts = []
  nterminals = ncols * nrows
  for i in range( nterminals ):
    src_x = i %  ncols
    src_y = i // ncols
    dst_x = ( i+1 ) %  ncols
    dst_y = ( ( i+1 ) % nterminals ) // ncols
    payload = [ x for x in range( i % 10 ) ]
    pkts.append( mk_pkt( src_x, src_y, dst_x, dst_y, payload ) )

  return pkts

#-------------------------------------------------------------------------
# test case table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                'msg_func        ncols  nrows' ),
  [ 'basic',        basic_pkts,     2,     2      ],
  [ 'basic4x4',     basic_pkts,     4,     4      ],
  [ 'neighbor2x2',  neighbor_pkts,  2,     2      ],
  [ 'neighbor2x3',  neighbor_pkts,  2,     3      ],
  [ 'neighbor3x3',  neighbor_pkts,  3,     3      ],
  [ 'neighbor4x4',  neighbor_pkts,  4,     4      ],
])

#-------------------------------------------------------------------------
# test driver
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_mflit_mesh( test_params, cmdline_opts ):
  ncols = test_params.ncols
  nrows = test_params.nrows
  pkts  = test_params.msg_func( ncols, nrows )

  src_pkts, dst_pkts = arrange_src_sink_pkts( TestHeader, ncols, nrows, pkts )

  th = TestHarness( TestHeader, TestPosition, ncols, nrows,
                    src_pkts, dst_pkts )
  run_sim( th, cmdline_opts )

#-------------------------------------------------------------------------
# packet strategy
#-------------------------------------------------------------------------

hex_words = [ 0x8badf00d, 0xdeadbeef, 0xfaceb00c, 0xdeadc0de ]

@st.composite
def pkt_strat( draw, ncols, nrows, max_plen=15 ):
  payload = draw( st.lists( st.sampled_from( hex_words ), min_size=0, max_size=max_plen ) )
  src_x   = draw( st.integers(0, ncols-1) )
  src_y   = draw( st.integers(0, nrows-1) )
  dst_x   = draw( st.integers(0, ncols-1) )
  dst_y   = draw( st.integers(0, nrows-1) )
  return mk_pkt( src_x, src_y, dst_x, dst_y, payload )

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
  ncols = st.integers(2, 4),
  nrows = st.integers(2, 4),
  pkts  = st.data(),
)
def test_pyh2( ncols, nrows, pkts, cmdline_opts ):
  pkts = pkts.draw( st.lists( pkt_strat( ncols, nrows ), min_size=1, max_size=100 ) )
  src_pkts, dst_pkts = arrange_src_sink_pkts( TestHeader, ncols, nrows, pkts )
  th = TestHarness( TestHeader, TestPosition, ncols, nrows,
                    src_pkts, dst_pkts )
  run_sim( th, cmdline_opts )
