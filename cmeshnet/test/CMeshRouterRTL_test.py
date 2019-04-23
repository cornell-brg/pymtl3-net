#=========================================================================
# CMeshRouterRTL_test.py
#=========================================================================
# Test for CMeshRouterRTL
#
# Author : Cheng Tan, Yanghui Ou
#   Date : April 16, 2019

from pymtl                        import *
from pclib.test.test_srcs         import TestSrcRTL
from pclib.test.test_sinks        import TestSinkRTL
from ocn_pclib.ifcs.Position      import *
from ocn_pclib.ifcs.Packet        import * 
from ocn_pclib.ifcs.Flit          import *
from pclib.test                   import TestVectorSimulator
from cmeshnet.CMeshRouterRTL      import CMeshRouterRTL
from meshnet.DORXMeshRouteUnitRTL import DORXMeshRouteUnitRTL
from meshnet.DORYMeshRouteUnitRTL import DORYMeshRouteUnitRTL
from router.ULVCUnitRTL           import ULVCUnitRTL
from router.InputUnitRTL          import InputUnitRTL

#-------------------------------------------------------------------------
# Test Vector
#-------------------------------------------------------------------------

def run_vector_test( model, test_vectors, mesh_wid=4, mesh_ht=4, 
                     pos_x=1, pos_y=1 ):
 
  def tv_in( model, test_vector ):

    MeshPos   = mk_mesh_pos( mesh_wid, mesh_ht )
    model.pos = MeshPos( pos_x, pos_y )

    for i in range( 8 ):
      if model.recv[i].rdy and test_vector[3][i]:
        pkt = mk_cmesh_pkt( 0, 0, test_vector[0][i]/4, test_vector[0][i]%4, 
                      test_vector[1], 1, test_vector[2][i] )
  
        model.recv[i].msg = pkt

        model.recv[i].en = 1
      elif model.recv[i].rdy == 0:
        model.recv[i].en = 0
        

    for i in range( model.num_outports ):
      model.send[i].rdy = 1

  def tv_out( model, test_vector ):

    for i in range( model.num_outports ):
      assert model.send[i].en == (test_vector[4][i] != 'x')
      if model.send[i].en == 1:
        pkt = model.send[i].msg
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
#     [dst]   term     payload          recv_rdy               send_msg
  [[4,4,7,4,5],0,[11,12,13,14,15],[1,1,1,0,1,0,0,0],[xx,xx,xx,xx,xx,xx,xx,xx]],
  [[4,4,7,9,5],1,[21,22,23,24,25],[1,1,1,1,1,0,0,0],[11,13,xx,xx,15,xx,xx,xx]],
  [[4,4,7,8,5],2,[31,32,33,34,35],[0,0,0,0,1,0,0,0],[12,23,xx,24,xx,25,xx,xx]],
  [[4,6,7,8,5],3,[41,42,43,44,45],[1,0,0,0,1,0,0,0],[21,23,xx,24,xx,xx,35,xx]],
  ]

  MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )
  model = CMeshRouterRTL( CMeshPacket, MeshPos, 8, 8 )

  run_vector_test( model, inputs_buffer, mesh_wid, mesh_ht, pos_x, pos_y )

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, MsgType, mesh_wid, mesh_ht, src_msgs, sink_msgs, 
                 src_initial, src_interval, sink_initial, sink_interval,
                 arrival_time=None ):

    MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )
    s.dut = CMeshRouterRTL( MsgType, MeshPos, 8, 8, RouteUnitType = DORYMeshRouteUnitRTL )

    s.srcs  = [ TestSrcRTL   ( MsgType, src_msgs[i],  src_initial,  src_interval  )
              for i in range ( 8 ) ]
    s.sinks = [ TestSinkRTL  ( MsgType, sink_msgs[i], sink_initial, sink_interval ) 
              for i in range ( 8 ) ]

    # Connections

    for i in range ( s.dut.num_outports ):
      s.connect( s.srcs[i].send, s.dut.recv[i]   )
      s.connect( s.dut.send[i],  s.sinks[i].recv )

    @s.update
    def up_pos():
      s.dut.pos = MeshPos(1,1)

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
    return s.dut.line_trace()

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

#             x,y,pl,dir,term
test_msgs = [[(0,0,11,0,0),(0,0,12,0,0),(0,1,13,2,0),(2,1,14,3,0),(0,0,15,0,0)],
             [(0,0,21,0,1),(0,2,22,1,1),(0,1,23,2,1),(2,1,24,3,1),(2,1,25,3,1)],
             [(0,2,31,1,2),(0,0,32,0,2),(0,1,33,2,2),(1,1,34,4,2),(1,1,35,4,2)]
            ]
result_msgs = [[],[],[],[],[],[],[],[]]

def test_normal_simple():

  src_packets = [[],[],[],[],[],[],[],[]]
  for item in test_msgs:
    for i in range( len( item ) ):
      (dst_x,dst_y,payload,dir_out,terminal) = item[i]
      pkt = mk_cmesh_pkt (0, 0, dst_x, dst_y, terminal, 1, payload)
      src_packets[7-dir_out].append( pkt )
      result_msgs[dir_out].append( pkt )

  th = TestHarness( CMeshPacket, 4, 4, src_packets, result_msgs, 0, 0, 0, 0 )
  run_sim( th )
