#=========================================================================
# MeshRouterFL_test.py
#=========================================================================
# Test for RouterFL
#
# Author : Cheng Tan
#   Date : May 18, 2019

import hypothesis
from hypothesis import strategies as st

from pymtl                        import *
from pclib.test.test_srcs         import TestSrcRTL
# from pclib.test.test_sinks        import TestSinkRTL
from ocn_pclib.test.net_sinks     import TestNetSinkRTL
from ocn_pclib.ifcs.Position      import mk_mesh_pos
from ocn_pclib.ifcs.Packet        import Packet, mk_pkt 
from ocn_pclib.ifcs.Flit          import *
from pclib.test                   import TestVectorSimulator
from meshnet.MeshRouterFL         import MeshRouterFL

from test_helpers import dor_routing

#-------------------------------------------------------------------------
# Test Vector
#-------------------------------------------------------------------------

def run_vector_test( model, test_vectors, mesh_wid=4, mesh_ht=4, 
                     pos_x=1, pos_y=1 ):
 
  def tv_in( model, test_vector ):

    MeshPos   = mk_mesh_pos( mesh_wid, mesh_ht )
    model.pos = MeshPos( pos_x, pos_y )

    for i in range( model.num_inports ):
#      pkt = mk_pkt( 0, 0, test_vector[0][i]/4, test_vector[0][i]%4, 
#                    1, test_vector[2][i] )
      pkt = mk_base_pkt( 0, test_vector[0][i], 1, test_vector[2][i] )
      flits = flitisize_mesh_flit( pkt, 1, mesh_wid, mesh_ht )

#      model.recv[i].msg = pkt
      model.recv[i].msg = flits[0]
      if model.recv[i].rdy:
        model.recv[i].en = 1

    for i in range( model.num_outports ):
      model.send[i].rdy = test_vector[1][i]

  def tv_out( model, test_vector ):
    for i in range( model.num_inports ):
      print 'i:', i, ';', model.recv[i].rdy, test_vector[3][i]
      assert model.recv[i].rdy == test_vector[3][i]

    for i in range( model.num_outports ):
      assert model.send[i].en == (test_vector[4][i] != 'x')
      if model.send[i].en == 1:
        pkt = model.send[i].msg.payload
        assert pkt.payload == test_vector[4][i]
  
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

def test_vector_Router_4_4X():

  mesh_wid = 4
  mesh_ht  = 4
  pos_x    = 1
  pos_y    = 1
  
  xx = 'x'
  inputs_buffer= [
#     [dst]      send_rdy       payload       recv_rdy      send_msg
  [[4,4,7,4,5],[0,0,0,0,0],[11,12,13,14,15],[1,1,1,1,1],[xx,xx,xx,xx,xx]],
  [[4,4,7,8,9],[0,0,0,0,0],[21,22,23,24,25],[1,1,1,1,1],[xx,xx,xx,xx,xx]],
  [[4,4,7,8,9],[1,1,1,1,1],[31,32,33,34,35],[0,0,0,0,0],[13,11,xx,xx,15]],
  [[4,6,7,8,9],[1,1,1,1,1],[41,42,43,44,45],[1,0,1,0,1],[23,12,xx,25,xx]],
  [[9,0,0,4,6],[1,1,0,1,1],[51,52,53,54,55],[0,1,1,0,1],[43,14,xx,45,xx]],
  ]

  MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )
  MeshFlit = mk_mesh_flit( 1, mesh_wid, mesh_ht )
  model = MeshRouterFL( MeshFlit, MeshPos, mesh_wid, mesh_ht, 'DORX' )

  run_vector_test( model, inputs_buffer, mesh_wid, mesh_ht, pos_x, pos_y )

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
    s.dut = MeshRouterFL( MsgType, MeshPos, mesh_wid, mesh_ht )

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
      #'|'.join( [ s.sinks[i].line_trace() for i in range(5) ] ), 
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

def test_normal_simple():

  src_packets = [[],[],[],[],[]]
  for item in test_msgs:
    for i in range( len( item ) ):
      (dst_x,dst_y,payload,dir_out) = item[i]
      pkt = mk_pkt (0, 0, dst_x, dst_y, 1, payload)
      src_packets[i].append( pkt )
      result_msgs[dir_out].append( pkt )

  th = TestHarness( Packet, 4, 4, 1, 1, src_packets, result_msgs, 0, 0, 0, 0 )
#  run_sim( th )

def test_self_simple():
  pkt = mk_pkt( 0, 0, 0, 0, 0, 0xdead )
  src_pkts  = [ [], [], [], [], [pkt] ]
  sink_pkts = [ [], [], [], [], [pkt] ]
  th = TestHarness( Packet, 4, 4, 0, 0, src_pkts, sink_pkts )
#  run_sim( th )

# Failing test cases captured by hypothesis
def test_h0():
  pos_x = 0
  pos_y = 0
  mesh_wid = 2
  mesh_ht  = 2
  pkt0 = mk_pkt( 0, 0, 1, 0, 0, 0xdead )
  pkt1 = mk_pkt( 0, 1, 1, 0, 0, 0xbeef )
  src_pkts  = [ [pkt1], [], [], [],           [pkt0] ]
  sink_pkts = [ [],     [], [], [pkt0, pkt1], []     ]
  th = TestHarness( 
    Packet, mesh_wid, mesh_ht, pos_x, pos_y, 
    src_pkts, sink_pkts
  )
#  run_sim( th )

def test_h1():
  pos_x, pos_y, mesh_wid, mesh_ht = 0, 0, 2, 2 
  pkt0 = mk_pkt( 0, 0, 0, 1, 0, 0xdead )
  src_pkts  = [ [],     [], [], [], [pkt0] ]
  sink_pkts = [ [pkt0], [], [], [], []     ]
  th = TestHarness( 
    Packet, mesh_wid, mesh_ht, pos_x, pos_y, 
    src_pkts, sink_pkts
  )
#  th.set_param( 
#    "top.dut.construct", 
#    RouteUnitType = DORXMeshRouteUnitRTL 
#  )
#  run_sim( th )

def test_h2():
  pos_x, pos_y, mesh_wid, mesh_ht = 0, 0, 2, 2 
  pkt0 = mk_pkt( 0, 0, 1, 0, 0, 0xdead )
  pkt1 = mk_pkt( 0, 1, 1, 0, 1, 0xbeef )
  pkt2 = mk_pkt( 0, 1, 1, 0, 2, 0xcafe )
              # N             S   W   E                   self
  src_pkts  = [ [pkt1, pkt2], [], [], [],                 [pkt0] ]
  sink_pkts = [ [],           [], [], [pkt1, pkt2, pkt0], []     ]
  th = TestHarness( 
    Packet, mesh_wid, mesh_ht, pos_x, pos_y, 
    src_pkts, sink_pkts
  )
#  th.set_param( 
#    "top.dut.construct", 
#    RouteUnitType = DORXMeshRouteUnitRTL 
#  )
#  run_sim( th, 10 )

def test_h3():
  pos_x, pos_y, mesh_wid, mesh_ht = 0, 1, 2, 2 
  pkt0 = mk_pkt( 0, 1, 0, 0, 0, 0xdead )
              # N   S   W   E   self
  src_pkts  = [ [], [], [], [], [pkt0] ]
  sink_pkts = [ [], [pkt0], [], [], [] ]
  th = TestHarness( 
    Packet, mesh_wid, mesh_ht, pos_x, pos_y, 
    src_pkts, sink_pkts
  )
#  th.set_param( 
#    "top.dut.construct", 
#    RouteUnitType = DORYMeshRouteUnitRTL 
#  )
#  run_sim( th, 10 )

#-------------------------------------------------------------------------
# Hypothesis test
#-------------------------------------------------------------------------

@st.composite
def mesh_pkt_strat( draw, mesh_wid, mesh_ht, routing_algo, pos_x, pos_y ):
  dst_x = draw( st.integers(0, mesh_wid-1) )
  dst_y = draw( st.integers(0, mesh_ht -1) )
  src_x = draw( st.integers(0, mesh_wid-1) )
  src_y = draw( st.integers(0, mesh_ht -1) )
  opaque  = draw( st.integers(0, 4) )
  payload = draw( st.sampled_from([ 0, 0xdeadbeef, 0xfaceb00c, 0xc001cafe ]) )
  pkt = mk_pkt( src_x, src_y, dst_x, dst_y, opaque, payload )
  tsrc, tsink = dor_routing( src_x, src_y, dst_x, dst_y, pos_x, pos_y, routing_algo ) 
  return tsrc, tsink, pkt

@hypothesis.settings( deadline = None )
@hypothesis.given(
  mesh_wid   = st.integers(2, 16),
  mesh_ht    = st.integers(2, 16),
  routing    = st.sampled_from(['x','y']),
  pos_x      = st.data(),
  pos_y      = st.data(),
  pkts       = st.data(),
  src_init   = st.integers(0, 20),
  src_inter  = st.integers(0, 5 ),
  sink_init  = st.integers(0, 20),
  sink_inter = st.integers(0, 5 ),
)
def test_hypothesis( mesh_wid, mesh_ht, routing, pos_x, pos_y, pkts, 
    src_init, src_inter, sink_init, sink_inter ):
  # Draw some numbers
  pos_x = pos_x.draw( st.integers(0,mesh_wid-1), label="pos_x" )
  pos_y = pos_y.draw( st.integers(0,mesh_wid-1), label="pos_y" )
  msgs  = pkts.draw( 
    st.lists( 
      mesh_pkt_strat(mesh_wid, mesh_ht, routing, pos_x, pos_y), 
      min_size = 1, max_size = 50 
    ),
    label = "msgs"
  )
  src_msgs  = [ [] for _ in range(5) ]
  sink_msgs = [ [] for _ in range(5) ]
  for src_id, sink_id, pkt in msgs:
    src_msgs [ src_id  ].append( pkt )
    sink_msgs[ sink_id ].append( pkt )

  # Configure the test harness
  # TODO: add delays
  th = TestHarness( Packet, mesh_wid, mesh_ht, pos_x, pos_y, 
                    src_msgs, sink_msgs,
                    src_init, src_inter,
                    sink_init, sink_inter )
#  th.set_param( "top.dut.construct", 
#    RouteUnitType = DORXMeshRouteUnitRTL if routing=='x' else DORYMeshRouteUnitRTL,
#    InputUnitType = InputUnitRTL
#  )
#  run_sim( th, 1000 )
