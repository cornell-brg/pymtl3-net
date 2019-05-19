#=========================================================================
# RingRouterCL_test.py
#=========================================================================
# Test for RingRouterCL
#
# Author : Yanghui Ou
#   Date : May 16, 2019

import hypothesis
from hypothesis import strategies as st

from pymtl                    import *
from pclib.test.test_srcs     import TestSrcCL
from ocn_pclib.test.net_sinks import TestNetSinkCL
from ocn_pclib.ifcs.Position  import mk_ring_pos
from ocn_pclib.ifcs.Packet    import BasePacket, mk_base_pkt 
from router.InputUnitCL       import InputUnitCL
from ringnet.RingRouterCL     import RingRouterCL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, 
                 MsgType       = None, 
                 nrouters      = 4, 
                 router_id     = 0,
                 src_msgs      = [], 
                 sink_msgs     = [], 
                 src_initial   = 0, 
                 src_interval  = 0, 
                 sink_initial  = 0, 
                 sink_interval = 0,
                 arrival_time  =[None, None, None, None, None] 
               ):

    print "=" * 74
    RingPos = mk_ring_pos( nrouters )
    s.dut = RingRouterCL( MsgType, RingPos )

    s.srcs  = [ TestSrcCL    ( src_msgs[i],  src_initial,  src_interval  )
                for i in range  ( s.dut.num_inports ) ]
    s.sinks = [ TestNetSinkCL( sink_msgs[i], sink_initial, 
                sink_interval ) for i in range ( s.dut.num_outports ) ]

    # Connections

    for i in range ( s.dut.num_outports ):
      s.connect( s.srcs[i].send, s.dut.recv[i]   )
      s.connect( s.dut.send[i],  s.sinks[i].recv )

    #TODO: provide pos for router... 
    @s.update
    def up_pos():
      s.dut.pos = RingPos( router_id )

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
    return "{} - {} - {}".format( 
      "|".join( [ s.srcs[i].line_trace() for i in range(3) ] ),
      s.dut.line_trace(),
      "|".join( [ s.sinks[i].line_trace() for i in range(3) ] ),
    )

#-------------------------------------------------------------------------
# run_sim
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

def test_normal_simple():

  pkt0 = mk_base_pkt( 1, 2, 0x01, 0xface )
  src_packets = [ 
   [ pkt0 ], 
   [], 
   [] 
  ]
  sink_packets = [ 
    [], 
    [ pkt0 ], 
    [] 
  ]

  th = TestHarness( BasePacket, 4, 1, src_packets, sink_packets, 0, 0, 0, 0 )
  run_sim( th )


#-------------------------------------------------------------------------
# Hypothesis test
#-------------------------------------------------------------------------

# @st.composite
# def mesh_pkt_strat( draw, mesh_wid, mesh_ht, routing_algo, pos_x, pos_y ):
#   dst_x = draw( st.integers(0, mesh_wid-1) )
#   dst_y = draw( st.integers(0, mesh_ht -1) )
#   src_x = draw( st.integers(0, mesh_wid-1) )
#   src_y = draw( st.integers(0, mesh_ht -1) )
#   opaque  = draw( st.integers(0, 4) )
#   payload = draw( st.sampled_from([ 0, 0xdeadbeef, 0xfaceb00c, 0xc001cafe ]) )
#   pkt = mk_pkt( src_x, src_y, dst_x, dst_y, opaque, payload )
#   tsrc, tsink = dor_routing( src_x, src_y, dst_x, dst_y, pos_x, pos_y, routing_algo ) 
#   return tsrc, tsink, pkt

# @hypothesis.settings( deadline = None )
# @hypothesis.given(
#   mesh_wid   = st.integers(2, 16),
#   mesh_ht    = st.integers(2, 16),
#   routing    = st.sampled_from(['x','y']),
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
#   # Draw some numbers
#   pos_x = pos_x.draw( st.integers(0,mesh_wid-1), label="pos_x" )
#   pos_y = pos_y.draw( st.integers(0,mesh_wid-1), label="pos_y" )
#   msgs  = pkts.draw( 
#     st.lists( 
#       mesh_pkt_strat(mesh_wid, mesh_ht, routing, pos_x, pos_y), 
#       min_size = 1, max_size = 50 
#     ),
#     label = "msgs"
#   )
#   src_msgs  = [ [] for _ in range(5) ]
#   sink_msgs = [ [] for _ in range(5) ]
#   for src_id, sink_id, pkt in msgs:
#     src_msgs [ src_id  ].append( pkt )
#     sink_msgs[ sink_id ].append( pkt )

#   # Configure the test harness
#   # TODO: add delays
#   th = TestHarness( Packet, mesh_wid, mesh_ht, pos_x, pos_y, 
#                     src_msgs, sink_msgs,
#                     src_init, src_inter,
#                     sink_init, sink_inter )
#   th.set_param( "top.dut.construct", 
#     RouteUnitType = DORXMeshRouteUnitRTL if routing=='x' else DORYMeshRouteUnitRTL,
#     InputUnitType = InputUnitRTL
#   )
#   run_sim( th, 1000 )
