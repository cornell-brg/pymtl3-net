"""
==========================================================================
MeshRouterCL_test.py
==========================================================================
Test cases for MeshRouterCL.

Author : Yanghui Ou
  Date : May 21, 2019
"""
from itertools import product

import hypothesis
import pytest
from hypothesis import strategies as st

from meshnet.DORXMeshRouteUnitCL import DORXMeshRouteUnitCL
from meshnet.MeshRouterCL import MeshRouterCL
from meshnet.MeshRouterFL import MeshRouterFL
from ocn_pclib.ifcs.packets import mk_mesh_pkt
from ocn_pclib.ifcs.positions import mk_mesh_pos
from ocn_pclib.test import run_sim
from ocn_pclib.test.net_sinks import TestNetSinkCL as TestSinkCL
from pymtl3 import *
from pymtl3.datatypes import strategies as pst
from pymtl3.stdlib.test.test_srcs import TestSrcCL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s,
    MsgType   = None,
    src_msgs  = [],
    sink_msgs = [],
    ncols  = 2,
    nrows   = 2 ,
    pos_x     = 0,
    pos_y     = 0,
  ):

    MeshPos = mk_mesh_pos( ncols, nrows )
    s.nrouters = ncols * nrows
    match_func = lambda a, b : a.src_x == a.src_x and a.src_y == b.src_y and \
                               a.dst_x == b.dst_x and a.dst_y == b.dst_y and \
                               a.opaque == b.opaque and a.payload == b.payload
    s.dut = MeshRouterCL( MsgType, MeshPos )

    s.srcs  = [ TestSrcCL( MsgType, src_msgs[i] )
                for i in range(5) ]
    s.sinks = [ TestSinkCL( MsgType, sink_msgs[i], match_func=match_func )
                for i in range(5) ]

    # Connections

    for i in range ( s.dut.num_outports ):
      s.srcs[i].send //= s.dut.recv[i]
      s.dut.send[i]  //= s.sinks[i].recv

    @s.update
    def up_pos():
      s.dut.pos = MeshPos( pos_x, pos_y )

  def done( s ):
    srcs_done = 1
    sinks_done = 1
    for i in range( s.dut.num_inports ):
      if s.srcs[i].done() == 0:
        srcs_done = 0
    for i in range( s.dut.num_outports ):
      if s.sinks[i].done() == 0:
        sinks_done = 0
    return srcs_done and sinks_done

  def line_trace( s ):
    return "{}".format( s.dut.line_trace() )

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@st.composite
def mesh_pkt_strat( draw, ncols, nrows, opaque_nbits=8, vc=1, payload_nbits=32 ):
  dst_x = draw( st.integers(0, ncols-1) )
  dst_y = draw( st.integers(0, nrows -1) )
  src_x = draw( st.integers(0, ncols-1) )
  src_y = draw( st.integers(0, nrows -1) )
  opaque  = draw( pst.bits( opaque_nbits ) )
  payload = draw( st.sampled_from([ 0, 0xdeadbeef, 0xfaceb00c, 0xc001cafe ]) )
  Pkt = mk_mesh_pkt( ncols, nrows, opaque_nbits, vc, payload_nbits )
  if vc==1:
    return Pkt( src_x, src_y, dst_x, dst_y, opaque, payload )
  else:
    return Pkt( src_x, src_y, dst_x, dst_y, opaque, 0, payload )

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

class MeshRouterCL_Tests:

  @classmethod
  def setup_class( s ):
    s.TestHarness = TestHarness

  @pytest.mark.parametrize(
    'pos_x, pos_y',
    product( [ 0, 1, 2, 3 ], [ 0, 1, 2, 3 ] ),
  )
  def test_simple4x4( s, pos_x, pos_y ):
    ncols = 4
    nrows  = 4
    Pkt = mk_mesh_pkt( ncols, nrows )
    router_fl = MeshRouterFL( pos_x, pos_y, dimension='x' )
    src_pkts = router_fl.arrange_src_pkts([
      #   src_x  y dst_x  y  opq payload
      Pkt(    0, 0,    3, 3, 0,  0xdeaddead ),
    ])
    dst_pkts = router_fl.route( src_pkts )
    th = s.TestHarness( Pkt, src_pkts, dst_pkts, ncols, nrows, pos_x, pos_y )
    run_sim( th )

  # Failing test cases captured by hypothesis

  def test_h0( s ):
    pos_x = 0; pos_y = 0; ncols = 2; nrows = 2
    Pkt = mk_mesh_pkt( ncols, nrows )
    router_fl = MeshRouterFL( pos_x, pos_y, dimension='x' )
    src_pkts = router_fl.arrange_src_pkts([
      #   src_x  y dst_x  y  opq payload
      Pkt(    0, 0,    1, 0, 0,  0xdeadbabe ),
      Pkt(    0, 0,    1, 0, 0,  0xdeadface ),
    ])
    dst_pkts = router_fl.route( src_pkts )
    th = s.TestHarness( Pkt, src_pkts, dst_pkts, ncols, nrows, pos_x, pos_y )
    run_sim( th )

  def test_h1( s ):
    pos_x = 0; pos_y = 0; ncols = 2; nrows = 2
    Pkt = mk_mesh_pkt( ncols, nrows )
    router_fl = MeshRouterFL( pos_x, pos_y, dimension='x' )
    src_pkts = router_fl.arrange_src_pkts([
      #   src_x  y dst_x  y  opq payload
      Pkt(    0, 0,    0, 1, 0,  0xdeadbabe ),
    ])
    dst_pkts = router_fl.route( src_pkts )
    th = s.TestHarness( Pkt, src_pkts, dst_pkts, ncols, nrows, pos_x, pos_y )
    run_sim( th )

#-------------------------------------------------------------------------
# Hypothesis test
#-------------------------------------------------------------------------

  @hypothesis.settings( deadline = None )
  @hypothesis.given(
    ncols   = st.integers(2, 16),
    nrows    = st.integers(2, 16),
    routing    = st.sampled_from(['x']), # TODO: add y after implementing DORY route unit
    pos_x      = st.data(),
    pos_y      = st.data(),
    pkts       = st.data(),
    src_init   = st.integers(0, 2 ),
    src_inter  = st.integers(0, 5 ),
    sink_init  = st.integers(0, 20),
    sink_inter = st.integers(0, 5 ),
  )
  def test_hypothesis( s, ncols, nrows, routing, pos_x, pos_y, pkts,
      src_init, src_inter, sink_init, sink_inter ):
    # Draw some numbers
    pos_x = pos_x.draw( st.integers(0,ncols-1), label="pos_x" )
    pos_y = pos_y.draw( st.integers(0,nrows-1), label="pos_y" )
    Pkt   = mk_mesh_pkt( ncols, nrows )
    router_fl = MeshRouterFL( pos_x, pos_y, dimension='x' )
    msgs  = pkts.draw(
      st.lists( mesh_pkt_strat( ncols, nrows ), min_size = 1, max_size = 50 ),
      label = "msgs"
    )
    src_pkts = router_fl.arrange_src_pkts( msgs )
    dst_pkts = router_fl.route( src_pkts )
    th = s.TestHarness( Pkt, src_pkts, dst_pkts, ncols, nrows, pos_x, pos_y )
    th.set_param( "top.src*.construct", initial_delay=src_init, interval_delay=src_init )
    th.set_param( "top.sink*.construct", initial_delay=sink_init, interval_delay=sink_init )
    run_sim( th, max_cycles=5000 )
