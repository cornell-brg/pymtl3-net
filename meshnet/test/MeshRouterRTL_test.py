#=========================================================================
# MeshRouterRTL_test.py
#=========================================================================
# Test for RouterRTL
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 10, 2019

import hypothesis
from hypothesis import strategies as st

from pymtl3                        import *
from pymtl3.stdlib.test.test_srcs  import TestSrcRTL
from ocn_pclib.test.net_sinks      import TestNetSinkRTL
from ocn_pclib.ifcs.positions      import mk_mesh_pos
from ocn_pclib.ifcs.packets         import  mk_mesh_pkt
from pymtl3.stdlib.test            import TestVectorSimulator
from meshnet.MeshRouterRTL        import MeshRouterRTL
from meshnet.DORXMeshRouteUnitRTL import DORXMeshRouteUnitRTL
from meshnet.DORYMeshRouteUnitRTL import DORYMeshRouteUnitRTL
from router.ULVCUnitRTL           import ULVCUnitRTL
from router.InputUnitRTL          import InputUnitRTL
from router.OutputUnitRTL          import OutputUnitRTL
from router.SwitchUnitRTL          import SwitchUnitRTL

from test_helpers import dor_routing

from pymtl3.passes.sverilog import ImportPass, TranslationPass
from pymtl3.passes import DynamicSim

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
    # print "src:", src_msgs
    # print "sink:", sink_msgs
    MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )
    s.dut = MeshRouterRTL( MsgType, MeshPos, InputUnitType = InputUnitRTL, 
        RouteUnitType = DORYMeshRouteUnitRTL )

    s.srcs  = [ TestSrcRTL    ( MsgType, src_msgs[i],  src_initial,  src_interval  )
                for i in range  ( s.dut.num_inports ) ]
    s.sinks = [ TestNetSinkRTL( MsgType, sink_msgs[i], sink_initial, 
                sink_interval ) for i in range ( s.dut.num_outports ) ]

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
#    for i in range( s.dut.num_inports ):
#      if s.srcs[i].done() == 0:
    for x in s.srcs:
      if x.done() == 0:
        srcs_done = 0
#    for i in range( s.dut.num_outports ):
#      if s.sinks[i].done() == 0:
    for x in s.sinks:
      if x.done() == 0:
        sinks_done = 0
    return srcs_done and sinks_done

  def line_trace( s ):
    return "{}".format(
      s.dut.line_trace(),
      #'|'.join( [ s.sinks[i].line_trace() for i in range(5) ] ), 
    )

#-------------------------------------------------------------------------
# run_rtl_sim
#-------------------------------------------------------------------------

def run_sim( test_harness, max_cycles=1000 ):

  # Create a simulator
  test_harness.elaborate()
  test_harness.dut.sverilog_translate = True
  test_harness.dut.sverilog_import = True
  test_harness.apply( TranslationPass() )
  test_harness = ImportPass()( test_harness )
#  test_harness.apply( SimpleSim )
  test_harness.apply( DynamicSim )
  test_harness.sim_reset()

  # Run simulation

  ncycles = 0
  print ""
  print "{}:{}".format( ncycles, test_harness.line_trace() )
  while not test_harness.done() and ncycles < max_cycles:
    test_harness.tick()
    ncycles += 1
    print "{}:{}".format( ncycles, test_harness.line_trace() )

  # Check timeout

  assert ncycles < max_cycles

  test_harness.tick()
  test_harness.tick()
  test_harness.tick()

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

#              x,y,pl,dir
test_msgs = [[(0,0,11,1),(0,0,12,1),(0,1,13,2),(2,1,14,3),(0,0,15,1)],
             [(0,0,21,1),(0,2,22,0),(0,1,23,2),(2,1,24,3),(2,1,25,3)],
             [(0,2,31,0),(0,0,32,1),(0,1,33,2),(1,1,34,4),(1,1,35,4)]
            ]
result_msgs = [[],[],[],[],[]]

def ttest_normal_simple():

  src_packets = [[],[],[],[],[]]
  for item in test_msgs:
    for i in range( len( item ) ):
      (dst_x,dst_y,payload,dir_out) = item[i]
      PacketType = mk_mesh_pkt (4, 4)
      pkt = PacketType (0, 0, dst_x, dst_y, 1, payload)
      src_packets[i].append( pkt )
      result_msgs[dir_out].append( pkt )

  th = TestHarness( PacketType, 4, 4, 1, 1, src_packets, result_msgs, 0, 0, 0, 0 )
  run_sim( th )

def ttest_self_simple():
  PacketType = mk_mesh_pkt(4, 4)
  pkt = PacketType( 0, 0, 0, 0, 0, 0xdead )
  src_pkts  = [ [], [], [], [], [pkt] ]
  sink_pkts = [ [], [], [], [], [pkt] ]
  th = TestHarness( PacketType, 4, 4, 0, 0, src_pkts, sink_pkts )
  run_sim( th )

# Failing test cases captured by hypothesis
def test_h0():
  pos_x = 0
  pos_y = 0
  mesh_wid = 2
  mesh_ht  = 2
  PacketType = mk_mesh_pkt( mesh_wid, mesh_ht )
  pkt0 = PacketType( 0, 0, 1, 0, 0, 0xbee1 )
  pkt1 = PacketType( 0, 1, 1, 0, 0, 0xbee2 )
  pkt2 = PacketType( 0, 1, 1, 0, 0, 0xbee3 )
  pkt3 = PacketType( 0, 1, 1, 0, 0, 0xbee4 )
  pkt4 = PacketType( 0, 1, 1, 0, 0, 0xbee5 )
  src_pkts  = [ [pkt1,pkt2,pkt3], [], [], [],           [pkt0,pkt4] ]
  sink_pkts = [ [],     [], [], [pkt0, pkt1,pkt2,pkt3,pkt4], []     ]
  th = TestHarness( 
    PacketType, mesh_wid, mesh_ht, pos_x, pos_y,
    src_pkts, sink_pkts
  )
  run_sim( th )

def ttest_h1():
  pos_x, pos_y, mesh_wid, mesh_ht = 0, 0, 2, 2 
  PacketType = mk_mesh_pkt( mesh_wid, mesh_ht )
  pkt0 = PacketType( 0, 0, 0, 1, 0, 0xdead )
  src_pkts  = [ [],     [], [], [], [pkt0] ]
  sink_pkts = [ [pkt0], [], [], [], []     ]
  th = TestHarness( 
    PacketType, mesh_wid, mesh_ht, pos_x, pos_y,
    src_pkts, sink_pkts
  )
  th.set_param( 
    "top.dut.construct", 
    RouteUnitType = DORYMeshRouteUnitRTL 
  )
  run_sim( th )

def ttest_h2():
  pos_x, pos_y, mesh_wid, mesh_ht = 0, 0, 2, 2 
  PacketType( mesh_wid, mesh_ht )
  pkt0 = PacketType( 0, 0, 1, 0, 0, 0xdead )
  pkt1 = PacketType( 0, 1, 1, 0, 1, 0xbeef )
  pkt2 = PacketType( 0, 1, 1, 0, 2, 0xcafe )
              # N             S   W   E                   self
  src_pkts  = [ [pkt1, pkt2], [], [], [],                 [pkt0] ]
  sink_pkts = [ [],           [], [], [pkt1, pkt2, pkt0], []     ]
  th = TestHarness( 
    PacketType, mesh_wid, mesh_ht, pos_x, pos_y,
    src_pkts, sink_pkts
  )
  th.set_param( 
    "top.dut.construct",
    RouteUnitType = DORYMeshRouteUnitRTL
  )
  run_sim( th, 10 )

def ttest_h3():
  pos_x, pos_y, mesh_wid, mesh_ht = 0, 1, 2, 2 
  PacketType = mk_mesh_pkt( mesh_wid, mesh_ht )
  pkt0 = PacketType( 0, 1, 0, 0, 0, 0xdead )
              # N   S   W   E   self
  src_pkts  = [ [], [], [], [], [pkt0] ]
  sink_pkts = [ [], [pkt0], [], [], [] ]
  th = TestHarness( 
    PacketType, mesh_wid, mesh_ht, pos_x, pos_y,
    src_pkts, sink_pkts
  )
  th.set_param( 
    "top.dut.construct", 
    RouteUnitType = DORYMeshRouteUnitRTL
  )
  run_sim( th, 10 )

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
# 
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
# 
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
