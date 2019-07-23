#=========================================================================
# TorusNetworkRTL_test.py
#=========================================================================
# Test for TorusNetworkRTL
#
# Author : Yanghui Ou, Cheng Tan
#   Date : July 1, 2019

import hypothesis
from hypothesis                         import strategies as st
from pymtl3                             import *
from pymtl3.stdlib.test.test_srcs       import TestSrcRTL
from ocn_pclib.test.net_sinks           import TestNetSinkRTL
from ocn_pclib.ifcs.flits               import *
from ocn_pclib.ifcs.packets             import mk_mesh_pkt
from ocn_pclib.ifcs.positions           import mk_mesh_pos
from torusnet.TorusNetworkRTL           import TorusNetworkRTL
from torusnet.TorusNetworkFL            import torusnet_fl

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, PktType, ncols, nrows, src_msgs, sink_msgs ):

    s.nrouters = ncols * nrows
    MeshPos = mk_mesh_pos( ncols, nrows )
    match_func = lambda a, b : a.payload == b.payload

    s.srcs  = [ TestSrcRTL   ( PktType, src_msgs[i] )
                for i in range ( s.nrouters ) ]
    s.dut   = TorusNetworkRTL( PktType, MeshPos, ncols, nrows, 0)
    s.sinks = [ TestNetSinkRTL  ( PktType, sink_msgs[i], match_func=match_func )
                for i in range ( s.nrouters ) ]

    # Connections
    for i in range ( s.nrouters ):
      s.connect( s.srcs[i].send, s.dut.recv[i]   )
      s.connect( s.dut.send[i],  s.sinks[i].recv )

  def done( s ):
    srcs_done  = True
    sinks_done = True
    for i in range( s.nrouters ):
      if not s.srcs[i].done():
        srcs_done = False
        break
      if not s.sinks[i].done():
        sinks_done = False
        break
    return srcs_done and sinks_done

  def line_trace( s ):
    return s.dut.line_trace()

#-------------------------------------------------------------------------
# mk_src_pkts
#-------------------------------------------------------------------------

def mk_src_pkts( ncols, nrows, lst ):
  nterminals = nrows * ncols
  src_pkts = [ [] for _ in range( nterminals ) ]
  for pkt in lst:
    src_id = int(pkt.src_x) + int(pkt.src_y) * ncols
    src_pkts[ src_id ].append( pkt )
  return src_pkts

#-------------------------------------------------------------------------
# mk_src_pkts
#-------------------------------------------------------------------------

@st.composite
def torus_pkt_strat( draw, ncols, nrows ):
  src_x = draw( st.integers(0, ncols-1), label="src_x" )
  src_y = draw( st.integers(0, nrows-1), label="src_y" )
  dst_x = draw( st.integers(0, ncols-1), label="dst_x" )
  dst_y = draw( st.integers(0, nrows-1), label="dst_y" )
  payload = draw( st.sampled_from([ 0xdeadface, 0xfaceb00c, 0xdeadbabe ]) )
  Pkt = mk_mesh_pkt( ncols, nrows, nvcs=2 )
  return Pkt( src_x, src_y, dst_x, dst_y, 0, 0, payload )

#=========================================================================
# Test cases
#=========================================================================

class TorusNetwork_Tests( object ):

  def run_sim( s, th, max_cycles=200 ):
    th.elaborate()
    th.apply( SimulationPass )
    th.sim_reset()

    # Run simulation
    ncycles = 0
    print ""
    print "{:3}:{}".format( ncycles, th.line_trace() )
    while not th.done() and ncycles < max_cycles:
      th.tick()
      ncycles += 1
      print "{:3}:{}".format( ncycles, th.line_trace() )

    # Check timeout
    assert ncycles < max_cycles

  def test_simple( s ):
    ncols = 2
    nrows = 2

    Pkt = mk_mesh_pkt( ncols, nrows, nvcs=2 )

    src_pkts = mk_src_pkts( ncols, nrows, [
      #    src_x  y  dst_x  y   opq vc payload
      Pkt(     1, 0,     0, 1,  0,  0, 0xfaceb00c ),
      Pkt(     1, 1,     1, 0,  0,  0, 0xdeadface ),
    ])
    dst_pkts = torusnet_fl( ncols, nrows, src_pkts )
    th = TestHarness( Pkt, ncols, nrows, src_pkts, dst_pkts )
    s.run_sim( th )

  def test_simple_3x3( s ):
    ncols = 3
    nrows = 3

    Pkt = mk_mesh_pkt( ncols, nrows, nvcs=2 )

    src_pkts = mk_src_pkts( ncols, nrows, [
      #    src_x  y  dst_x  y   opq vc payload
      Pkt(     1, 0,     0, 2,  0,  0, 0xfaceb00c ),
      #Pkt(     1, 1,     1, 0,  0,  0, 0xdeadface ),
    ])
    dst_pkts = torusnet_fl( ncols, nrows, src_pkts )
    th = TestHarness( Pkt, ncols, nrows, src_pkts, dst_pkts )
    s.run_sim( th )

  def test_simple_5x5( s ):
    ncols = 5
    nrows = 5

    Pkt = mk_mesh_pkt( ncols, nrows, nvcs=2 )

    src_pkts = mk_src_pkts( ncols, nrows, [
      #    src_x  y  dst_x  y   opq vc payload
      Pkt(     1, 0,     0, 4,  0,  0, 0xfaceb00c ),
      #Pkt(     1, 1,     1, 0,  0,  0, 0xdeadface ),
    ])
    dst_pkts = torusnet_fl( ncols, nrows, src_pkts )
    th = TestHarness( Pkt, ncols, nrows, src_pkts, dst_pkts )
    s.run_sim( th )

  @hypothesis.settings( deadline=None, max_examples=5 )
  # @hypothesis.reproduce_failure('4.24.4', 'AAMDAQEAAAQAAA==') #(1:0)>(0:4)
  @hypothesis.given(
    ncols = st.integers(2, 8),
    nrows = st.integers(2, 8),
    pkts  = st.data(),
  )
  def test_hypothesis( s, ncols, nrows, pkts ):
    Pkt = mk_mesh_pkt( ncols, nrows, nvcs=2 )

    pkts_lst = pkts.draw(
      st.lists( torus_pkt_strat( ncols, nrows ), max_size=4 ),
      label= "pkts"
    )

    src_pkts = mk_src_pkts( ncols, nrows, pkts_lst )
    dst_pkts = torusnet_fl( ncols, nrows, src_pkts )
    th = TestHarness( Pkt, ncols, nrows, src_pkts, dst_pkts )
    s.run_sim( th, max_cycles=20 )
