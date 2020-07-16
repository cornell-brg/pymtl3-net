'''
==========================================================================
PitonMeshNet_test.py
==========================================================================
Test cases for PitonMeshNet.

Author : Yanghui Ou
  Date : Mar 6, 2020
'''
import os
import pytest
import hypothesis
from hypothesis import strategies as st
from pymtl3 import *
from pymtl3.stdlib.test_utils import mk_test_case_table
from ocnlib.utils import run_sim
from ocnlib.packets import MflitPacket as Packet
from ocnlib.test.test_srcs import MflitPacketSourceRTL as TestSource
from ocnlib.test.test_sinks import MflitPacketSinkRTL as TestSink

from ..PitonNoCHeader import PitonNoCHeader
from ..PitonMeshNet import PitonMeshNet

#-------------------------------------------------------------------------
# TestPosition
#-------------------------------------------------------------------------

@bitstruct
class PitonPosition:
  pos_x : Bits8
  pos_y : Bits8

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, ncols, nrows, src_pkts, sink_pkts ):
    nterminals = ncols * nrows

    s.src  = [ TestSource( PitonNoCHeader, src_pkts[i] ) for i in range( nterminals+1 ) ]
    s.dut  = PitonMeshNet( PitonPosition, ncols, nrows )
    s.sink = [ TestSink( PitonNoCHeader, sink_pkts[i] ) for i in range( nterminals+1 ) ]

    for i in range( nterminals ):
      s.src[i].send //= s.dut.recv[i]
      s.dut.send[i] //= s.sink[i].recv

    s.src[ nterminals ].send //= s.dut.offchip_recv
    s.dut.offchip_send       //= s.sink[ nterminals ].recv

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

def mk_pkt( src_offchip, src_x, src_y, dst_offchip, dst_x, dst_y,
            payload=[], fbits=0, mtype=0, mshr=0, opt1=0 ):
  chipid      = b14(1) << 13 if dst_offchip else b14(0)
  plen        = len( payload )
  header      = PitonNoCHeader( chipid, dst_x, dst_y, fbits, plen, mtype, mshr, opt1 )
  header_bits = header.to_bits()
  flits       = [ header_bits ] + payload
  pkt         = Packet( PitonNoCHeader, flits )
  pkt.src_offchip = src_offchip
  pkt.src_x = src_x
  pkt.src_y = src_y
  return pkt

#-------------------------------------------------------------------------
# arrange_src_sink_pkts
#-------------------------------------------------------------------------

def arrange_src_sink_pkts( ncols, nrows, pkt_lst ):
  nterminals = ncols * nrows
  src_pkts  = [ [] for _ in range( nterminals+1 ) ]
  sink_pkts = [ [] for _ in range( nterminals+1 ) ]

  for pkt in pkt_lst:
    header = PitonNoCHeader.from_bits( pkt.flits[0] )
    src_id = nterminals if pkt.src_offchip else pkt.src_x + pkt.src_y * ncols
    dst_id = nterminals if header.chipid[13] else header.xpos.uint() + header.ypos.uint() * ncols
    src_pkts [ src_id ].append( pkt )
    sink_pkts[ dst_id ].append( pkt )

  return src_pkts, sink_pkts

#-------------------------------------------------------------------------
# sanity check
#-------------------------------------------------------------------------

def test_sanity_check():
  net = PitonMeshNet( PitonPosition, ncols=2, nrows=2 )
  net.elaborate()
  net.apply( DefaultPassGroup() )
  net.sim_reset()
  net.sim_tick()

n = False
y = True

#-------------------------------------------------------------------------
# test case: basic
#-------------------------------------------------------------------------

def basic_pkts( ncols, nrows ):
  return [
    #      src                    dst
    #      off       x  y       | off      x  y        payload
    mk_pkt( n,       0, 0,        n, ncols-1, nrows-1, [ 0x8badf00d             ] ),
    mk_pkt( n, ncols-1, nrows-1,  n,       0, 0,       [ 0x8badf00d, 0xdeadbeef ] ),
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
    pkts.append( mk_pkt( n, src_x, src_y, n, dst_x, dst_y, payload ) )

  return pkts

#-------------------------------------------------------------------------
# test case table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                'msg_func        ncols  nrows' ),
  [ 'basic',        basic_pkts,     2,     2      ],
  [ 'basic4x4',     basic_pkts,     4,     4      ],
  [ 'basic2x7',     basic_pkts,     2,     7      ],
  [ 'neighbor2x2',  neighbor_pkts,  2,     2      ],
  [ 'neighbor2x3',  neighbor_pkts,  2,     3      ],
  [ 'neighbor3x3',  neighbor_pkts,  3,     3      ],
  [ 'neighbor4x4',  neighbor_pkts,  4,     4      ],
  [ 'neighbor2x7',  neighbor_pkts,  2,     7      ],
])

#-------------------------------------------------------------------------
# test driver
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_piton_mesh( test_params, cmdline_opts ):
  ncols = test_params.ncols
  nrows = test_params.nrows
  pkts  = test_params.msg_func( ncols, nrows )

  src_pkts, dst_pkts = arrange_src_sink_pkts( ncols, nrows, pkts )

  th = TestHarness( ncols, nrows, src_pkts, dst_pkts )
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
  return mk_pkt( n, src_x, src_y, n, dst_x, dst_y, payload )

#-------------------------------------------------------------------------
# pyh2 test
#-------------------------------------------------------------------------

@hypothesis.settings( deadline=None, max_examples=20 )
@hypothesis.given(
  ncols = st.integers(2, 4),
  nrows = st.integers(2, 4),
  pkts  = st.data(),
)
def test_pyh2( ncols, nrows, pkts, cmdline_opts ):
  pkts = pkts.draw( st.lists( pkt_strat( ncols, nrows ), min_size=1, max_size=100 ) )
  src_pkts, dst_pkts = arrange_src_sink_pkts( ncols, nrows, pkts )
  th = TestHarness( ncols, nrows, src_pkts, dst_pkts )
  run_sim( th, cmdline_opts )
