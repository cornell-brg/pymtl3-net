#=========================================================================
# DORYRouteUnitRTL_test.py
#=========================================================================
# Test for DORYRouteUnitRTL
#
# Author : Yanghui Ou, Cheng Tan
#   Date : Mar 25, 2019

from pymtl3                        import *
from pymtl3.stdlib.test                   import TestVectorSimulator
#from ocn_pclib.ifcs.Packet        import *
from ocn_pclib.ifcs.Flit          import *
from ocn_pclib.ifcs.Position      import mk_mesh_pos
from ocn_pclib.ifcs.packets       import mk_mesh_pkt
from pymtl3.passes.PassGroups      import SimpleSim
from pymtl3.stdlib.test.test_srcs         import TestSrcRTL
from pymtl3.stdlib.test.test_sinks        import TestSinkRTL
from meshnet.DORYMeshRouteUnitRTL import DORYMeshRouteUnitRTL 
from pymtl3.passes.VcdGenerationPass import VcdGenerationPass

#-------------------------------------------------------------------------
# Driver function for TestVectorSimulator
#-------------------------------------------------------------------------

def run_test( model, mesh_wid, mesh_ht, router_pos, test_vectors ):
 
  def tv_in( model, test_vector ):

    dst_x   = test_vector[0]
    dst_y   = test_vector[1]
    opaque  = test_vector[2]
    payload = test_vector[3]

    pkt = mk_pkt( 0, 0, dst_x, dst_y, opaque, payload )

    model.pos = router_pos
    model.get.msg = pkt
    model.get.rdy = test_vector[5]

    for i in range( model.num_outports ):
      model.give[i].en = test_vector[7][i]

  def tv_out( model, test_vector ):

    assert model.get.en == test_vector[4]
    for i in range( 5 ):
      assert model.give[i].rdy == test_vector[6][i]
      if test_vector[6][i]:
        assert model.give[i].msg.opaque  == test_vector[2]
        assert model.give[i].msg.payload == test_vector[3]
  
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )

  sim.run_test()

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

def test_route_unit():
  mesh_wid = 2
  mesh_ht  = 2

  MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )
  PacketType = mk_mesh_pkt( mesh_wid, mesh_ht, 1, 8, 32 )
  model = DORYMeshRouteUnitRTL( PacketType, MeshPos, 5 )

#  model.apply( VcdGenerationPass() )
  # Test for Y-DOR routing algorithm

  run_test( model, mesh_wid, mesh_ht, MeshPos( 0, 0 ), [
   # dst_x  dst_y  opaque  payload get_en get_rdy   give_rdy       give_en 
   [   1,     1,     1,       9,      0,     0,    [0,0,0,0,0],  [0,0,0,0,0] ],
   [   0,     1,     1,       7,      1,     1,    [1,0,0,0,0],  [1,0,0,0,0] ],
   [   1,     0,     1,       3,      0,     1,    [0,0,0,1,0],  [0,0,0,0,0] ],
   [   0,     0,     1,       6,      0,     1,    [0,0,0,0,1],  [0,0,0,0,0] ],
   [   0,     0,     1,       4,      0,     0,    [0,0,0,0,0],  [0,0,0,0,0] ],
   [   0,     0,     1,       4,      1,     1,    [0,0,0,0,1],  [0,0,0,0,1] ],
  ] )

def test_route_unit3x3():
  mesh_wid = 3
  mesh_ht  = 3

  MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )

  PacketType = mk_mesh_pkt( mesh_wid, mesh_ht, 1, 8, 32 )
  model = DORYMeshRouteUnitRTL( PacketType, MeshPos )

  # Test for Y-DOR routing algorithm

  run_test( model, mesh_wid, mesh_ht, MeshPos( 1, 1 ), [
   # dst_x  dst_y  opaque  payload get_en get_rdy   give_rdy       give_en 
   [   1,     1,     1,       9,      0,     1,    [0,0,0,0,1],  [0,0,0,0,0] ],
   [   0,     1,     1,       7,      0,     1,    [0,0,1,0,0],  [0,0,0,0,0] ],
   [   1,     0,     1,       3,      0,     1,    [0,1,0,0,0],  [0,0,0,0,0] ],
   [   0,     0,     1,       6,      0,     1,    [0,1,0,0,0],  [0,0,0,0,0] ],
   [   1,     1,     1,       4,      0,     0,    [0,0,0,0,0],  [0,0,0,0,0] ],
   [   1,     1,     1,       4,      1,     1,    [0,0,0,0,1],  [0,0,0,0,1] ],
  ] )

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, MsgType, src_msgs, sink_msgs, src_initial,
                 src_interval, sink_initial, sink_interval,
                 arrival_time=None ):

    mesh_wid = 4
    mesh_ht  = 4
  
    MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )
    s.dut = DORYMeshRouteUnitRTL( MsgType, MeshPos )
    s.dut.pos = MeshPos( 1, 1 )

    s.src   = TestSrcRTL   ( MsgType, src_msgs,  src_initial,  src_interval  )
    s.sinks = [ TestSinkRTL  ( MsgType, sink_msgs[i], sink_initial, sink_interval, arrival_time[i] )
                for i in range ( s.dut.num_outports ) ]

    # Connections
    s.connect( s.src.send.msg, s.dut.get.msg )

    for i in range ( s.dut.num_outports ):
      s.connect( s.dut.give[i].msg, s.sinks[i].recv.msg )

    @s.update
    def up_give_en():
      for i in range (s.dut.num_outports):
        if s.dut.give[i].rdy and s.sinks[i].recv.rdy:
          s.dut.give[i].en  = 1
          s.sinks[i].recv.en = 1
        else:
          s.dut.give[i].en  = 0
          s.sinks[i].recv.en = 0

    # FIXME: connect send to get
    # s.connect( s.src.send.rdy, Bits1( 1 )    )
    # s.connect( s.dut.get.rdy,  s.src.send.en )

  def done( s ):
    sinks_done = 1
    for i in range( s.dut.num_outports ):
      if s.sinks[i].done() == 0:
        sinks_done = 0
    return s.src.done() and sinks_done

  def line_trace( s ):
    return s.src.line_trace() + "-> | " + s.dut.line_trace() + \
                               " | -> " + s.sinks[0].line_trace()

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

#               x,y,pl,dir
test_msgs   = [(0,0,101,0), (0,2,102,1), (0,1,103,2), (2,1,104,3), 
               (1,1,105,4), (1,1,106,4)]
result_msgs = [ [], [], [], [], [] ]

arrival_time = [ [1], [2], [3], [4], [5,6] ]

# def test_normal_simple():
# 
#   src_packets = []
#   for ( dst_x, dst_y, payload, dir_out ) in test_msgs:
#     pkt = mk_pkt (0, 0, dst_x, dst_y, 1, payload)
#     src_packets.append( pkt )
#     result_msgs[dir_out].append ( pkt )
# 
#   th = TestHarness( Packet, src_packets, result_msgs, 0, 0, 0, 0,
#                     arrival_time )
#   run_sim( th )
