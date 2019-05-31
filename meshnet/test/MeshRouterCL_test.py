#=========================================================================
# MeshRouterCL_test.py
#=========================================================================
# Test for RouterCL
#
# Author : Yanghui Ou
#   Date : May 21, 2019

import hypothesis
from hypothesis import strategies as st

from pymtl3                       import *
from pymtl3.stdlib.test.test_srcs        import TestSrcCL
from ocn_pclib.test.net_sinks    import TestNetSinkCL
from ocn_pclib.ifcs.positions    import mk_mesh_pos
from ocn_pclib.ifcs.packets      import mk_mesh_pkt
from meshnet.MeshRouterCL        import MeshRouterCL
from meshnet.MeshRouteUnitXDorCL import MeshRouteUnitXDorCL
from router.InputUnitCL          import InputUnitCL

from test_helpers import dor_routing

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, 
                 MsgType       = None, 
                 mesh_wid      = 2, 
                 mesh_ht       = 2 , 
                 pos_x         = 0,
                 pos_y         = 0,
                 src_msgs      = [], 
                 sink_msgs     = [], 
                 src_initial   = 0, 
                 src_interval  = 0, 
                 sink_initial  = 0, 
                 sink_interval = 0,
                 arrival_time  =[None, None, None, None, None] 
               ):

    print "=" * 74
    MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )
    s.dut = MeshRouterCL( MsgType, MeshPos )

    s.srcs  = [ TestSrcCL( src_msgs[i],  src_initial,  src_interval  )
                for i in range  ( s.dut.num_inports ) ]
    s.sinks = [ TestNetSinkCL( sink_msgs[i], sink_initial, sink_interval ) 
                for i in range ( s.dut.num_outports ) ]

    # Connections

    for i in range ( s.dut.num_outports ):
      s.connect( s.srcs[i].send, s.dut.recv[i]   )
      s.connect( s.dut.send[i],  s.sinks[i].recv )

    #TODO: provide pos for router... 
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
    return "{}".format( 
      s.dut.line_trace(), 
    )

#-------------------------------------------------------------------------
# run_rtl_sim
#-------------------------------------------------------------------------

def run_sim( test_harness, max_cycles=100 ):

  # Create a simulator

  test_harness.apply( SimpleSim )
  test_harness.sim_reset()

  # Run simulation

  ncycles = 0
  print ""
  print "{:2}:{}".format( ncycles, test_harness.line_trace() )
  while not test_harness.done() and ncycles < max_cycles:
    test_harness.tick()
    ncycles += 1
    print "{:2}:{}".format( ncycles, test_harness.line_trace() )

  # Check timeout

  assert ncycles < max_cycles

  test_harness.tick()
  test_harness.tick()
  test_harness.tick()

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

# TestPkt = mk_mesh_pkt( 4, 4 )
# 
# def test_self_simple():
#   pkt = TestPkt( 0, 0, 0, 0, 0, 0xdead )
#   src_pkts  = [ [], [], [], [], [pkt] ]
#   sink_pkts = [ [], [], [], [], [pkt] ]
#   th = TestHarness( TestPkt, 4, 4, 0, 0, src_pkts, sink_pkts )
#   run_sim( th )
# 
# # Failing test cases captured by hypothesis
# def test_h0():
#   pos_x = 0
#   pos_y = 0
#   mesh_wid = 2
#   mesh_ht  = 2
#   pkt0 = TestPkt( 0, 0, 1, 0, 0, 0xdead )
#   pkt1 = TestPkt( 0, 1, 1, 0, 0, 0xbeef )
#   src_pkts  = [ [pkt1], [], [], [],           [pkt0] ]
#   sink_pkts = [ [],     [], [], [pkt0, pkt1], []     ]
#   th = TestHarness( 
#     TestPkt, mesh_wid, mesh_ht, pos_x, pos_y, 
#     src_pkts, sink_pkts
#   )
#   run_sim( th )
# 
# def test_h1():
#   pos_x, pos_y, mesh_wid, mesh_ht = 0, 0, 2, 2 
#   pkt0 = TestPkt( 0, 0, 0, 1, 0, 0xdead )
#   src_pkts  = [ [],     [], [], [], [pkt0] ]
#   sink_pkts = [ [pkt0], [], [], [], []     ]
#   th = TestHarness( 
#     TestPkt, mesh_wid, mesh_ht, pos_x, pos_y, 
#     src_pkts, sink_pkts
#   )
#   run_sim( th )
# 
# def test_h2():
#   pos_x, pos_y, mesh_wid, mesh_ht = 0, 0, 2, 2 
#   pkt0 = TestPkt( 0, 0, 1, 0, 0, 0xdead )
#   pkt1 = TestPkt( 0, 1, 1, 0, 1, 0xbeef )
#   pkt2 = TestPkt( 0, 1, 1, 0, 2, 0xcafe )
#               # N             S   W   E                   self
#   src_pkts  = [ [pkt1, pkt2], [], [], [],                 [pkt0] ]
#   sink_pkts = [ [],           [], [], [pkt1, pkt2, pkt0], []     ]
#   th = TestHarness( 
#     TestPkt, mesh_wid, mesh_ht, pos_x, pos_y, 
#     src_pkts, sink_pkts
#   )
#   run_sim( th, 10 )

# def test_h3():
#   pos_x, pos_y, mesh_wid, mesh_ht = 0, 1, 2, 2 
#   pkt0 = TestPkt( 0, 1, 0, 0, 0, 0xdead )
#               # N   S   W   E   self
#   src_pkts  = [ [], [], [], [], [pkt0] ]
#   sink_pkts = [ [], [pkt0], [], [], [] ]
#   th = TestHarness( 
#     TestPkt, mesh_wid, mesh_ht, pos_x, pos_y, 
#     src_pkts, sink_pkts
#   )
#   th.set_param( 
#     "top.dut.construct", 
#     RouteUnitType = DORYMeshRouteUnitRTL 
#   )
#   run_sim( th, 10 )

#-------------------------------------------------------------------------
# Hypothesis test
#-------------------------------------------------------------------------

# @st.composite
# def mesh_pkt_strat( draw, PktType, mesh_wid, mesh_ht, routing_algo, pos_x, pos_y ):
#   dst_x = draw( st.integers(0, mesh_wid-1) )
#   dst_y = draw( st.integers(0, mesh_ht -1) )
#   src_x = draw( st.integers(0, mesh_wid-1) )
#   src_y = draw( st.integers(0, mesh_ht -1) )
#   opaque  = draw( st.integers(0, 4) )
#   payload = draw( st.sampled_from([ 0, 0xdeadbeef, 0xfaceb00c, 0xc001cafe ]) )
#   pkt = PktType( src_x, src_y, dst_x, dst_y, opaque, payload )
#   tsrc, tsink = dor_routing( src_x, src_y, dst_x, dst_y, pos_x, pos_y, routing_algo ) 
#   return tsrc, tsink, pkt
# 
# @hypothesis.settings( deadline = None )
# @hypothesis.given(
#   mesh_wid   = st.integers(2, 16),
#   mesh_ht    = st.integers(2, 16),
#   routing    = st.sampled_from(['x']),
#   pos_x      = st.data(),
#   pos_y      = st.data(),
#   pkts       = st.data(),
#   src_init   = st.integers(0, 20),
#   src_inter  = st.integers(0, 5 ),
#   sink_init  = st.integers(0, 20),
#   sink_inter = st.integers(0, 5 ),
# )
# def test_hypothesis( mesh_wid, mesh_ht, routing, pos_x, pos_y, pkts, 
#     src_init, src_inter, sink_init, sink_inter ):
#   PktType = mk_mesh_pkt( mesh_wid, mesh_ht )
#   # Draw some numbers
#   pos_x = pos_x.draw( st.integers(0,mesh_wid-1), label="pos_x" )
#   pos_y = pos_y.draw( st.integers(0,mesh_wid-1), label="pos_y" )
#   msgs  = pkts.draw( 
#     st.lists( 
#       mesh_pkt_strat( PktType, mesh_wid, mesh_ht, routing, pos_x, pos_y ), 
#       min_size = 1, max_size = 50 
#     ),
#     label = "msgs"
#   )
#   src_msgs  = [ [] for _ in range(5) ]
#   sink_msgs = [ [] for _ in range(5) ]
#   for src_id, sink_id, pkt in msgs:
#     src_msgs [ src_id  ].append( pkt )
#     sink_msgs[ sink_id ].append( pkt )
# 
#   # Configure the test harness
#   th = TestHarness( PktType, mesh_wid, mesh_ht, pos_x, pos_y, 
#                     src_msgs, sink_msgs,
#                     src_init, src_inter,
#                     sink_init, sink_inter )
#  #  th.set_param( "top.dut.construct", 
#  #    RouteUnitType = DORXMeshRouteUnitRTL if routing=='x' else DORYMeshRouteUnitRTL,
#  #    InputUnitType = InputUnitRTL
#  #  )
  run_sim( th, 1000 )
