#=========================================================================
# RouterRTL_test.py
#=========================================================================
# Test for RouterRTL
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 10, 2019

import tempfile
from pymtl                       import *
from router.MeshRouterRTL        import MeshRouterRTL
from router.InputUnitRTL         import InputUnitRTL
from router.DORXMeshRouteUnitRTL import DORXMeshRouteUnitRTL
from router.DORYMeshRouteUnitRTL import DORYMeshRouteUnitRTL
from router.SwitchUnitRTL        import SwitchUnitRTL
from router.OutputUnitRTL        import OutputUnitRTL
from ocn_pclib.rtl.queues        import NormalQueueRTL

from pclib.test.test_srcs         import TestSrcRTL
from pclib.test.test_sinks        import TestSinkRTL

from ocn_pclib.ifcs.Position     import *
from ocn_pclib.ifcs.Packet       import Packet, mk_pkt

from pclib.test                  import TestVectorSimulator
from Configs                     import configure_network

#-------------------------------------------------------------------------
# Test Vector
#-------------------------------------------------------------------------
def run_vector_test( model, test_vectors ):
 
  def tv_in( model, test_vector ):

    mesh_wid = 4
    mesh_ht  = 4
    MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )

    model.pos = MeshPos( 1, 1 )

    for i in range ( model.num_inports ):
      pkt = mk_pkt(0, 0, test_vector[0][i]/4, test_vector[0][i]%4, 
                   1, test_vector[2][i])
      model.recv[i].msg = pkt
      if model.recv[i].rdy:
        model.recv[i].en = 1

    for i in range( model.num_outports ):
      model.send[i].rdy = test_vector[1][i]

  def tv_out( model, test_vector ):
    for i in range( model.num_inports ):
#      print 'model.recv[',i,'].rdy:',model.recv[i].rdy,' == test_vector[4][',i,']:',test_vector[3][i]
      assert model.recv[i].rdy == test_vector[3][i]

    for i in range (model.num_outports):
#      print 'model.send[',i,'].en:',model.send[i].en,' == (test_vector[5][',i,']:',test_vector[4][i]
#      print 'model.switch_units[',i,'].send.en:',model.send[i].en,' == (test_vector[5][',i,']:',test_vector[5][i]
      assert model.send[i].en == (test_vector[4][i] != 'x')
      if model.send[i].en == 1:
#        print '  model.send[',i,'].msg.payload:',model.send[i].msg.payload,' == test_vector[4][',i,']:',test_vector[4][i]
        assert model.send[i].msg.payload == test_vector[4][i]
  
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

def test_vector_Router( dump_vcd, test_verilog ):

  configs = configure_network()

  if configs.routing_strategy == 'DORX':
    RouteUnitType = DORXMeshRouteUnitRTL
  elif configs.routing_strategy == 'DORY':
    RouteUnitType = DORYMeshRouteUnitRTL
  else:
    print 'Please specific a valid Routing strategy!'

  xx = 'x'
  inputs_buffer= [
# [dst_x,dst_y] send_rdy       payload       recv_rdy      send_msg
  [[4,4,7,4,5],[0,0,0,0,0],[11,12,13,14,15],[1,1,1,1,1],[xx,xx,xx,xx,xx]],
  [[4,4,7,8,9],[0,0,0,0,0],[21,22,23,24,25],[1,1,1,1,1],[xx,xx,xx,xx,xx]],
  [[4,4,7,8,9],[1,1,1,1,1],[31,32,33,34,35],[0,0,0,0,0],[11,13,xx,xx,15]],
  [[4,6,7,8,9],[1,1,1,1,1],[41,42,43,44,45],[1,0,1,0,1],[12,23,xx,25,xx]],
  [[9,0,0,4,6],[1,1,0,1,1],[51,52,53,54,55],[1,1,1,0,1],[14,43,xx,45,xx]],
  ]

  mesh_wid = 4
  mesh_ht  = 4

  MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )

  model = MeshRouterRTL( Packet, MeshPos, RouteUnitType )
#  for i in range ( 5 ):
#    queue_path = "top.input_units[" + str(i) + "].elaborate.QueueType"
#    model.set_parameter( queue_path, NormalQueueRTL )

  run_vector_test(model, inputs_buffer)

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
    s.dut = MeshRouterRTL( MsgType, MeshPos, DORYMeshRouteUnitRTL )
#    s.pos = MeshPos(1,1)
#    s.dut.pos = MeshPos( 1, 1 )

    s.srcs  = [ TestSrcRTL   ( MsgType, src_msgs[i],  src_initial,  src_interval  )
              for i in range ( s.dut.num_inports ) ]
    s.sinks = [ TestSinkRTL  ( MsgType, sink_msgs[i], sink_initial, 
              sink_interval, arrival_time[i]) for i in range ( s.dut.num_outports ) ]

    # Connections

    for i in range ( s.dut.num_outports ):
      s.connect( s.srcs[i].send, s.dut.recv[i]   )
      s.connect( s.dut.send[i],  s.sinks[i].recv )

    #TODO: provide pos for router... 
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
#              x,y,pl,dir
test_msgs = [[(0,0,11,0),(0,0,12,0),(0,1,13,2),(2,1,14,3),(0,0,15,0)],
             [(0,0,21,0),(0,2,22,1),(0,1,23,2),(2,1,24,3),(2,1,25,3)],
             [(0,2,31,1),(0,0,32,0),(0,1,33,2),(1,1,34,4),(1,1,35,4)]
            ]
result_msgs = [[],[],[],[],[]]

# note that need to yield one cycle for reset
arrival_pipes = [[2,3,4,5,6],[3,4],[2,3,4],[2,3,4],[4,5]]

def test_normal_simple():

  src_packets = [[],[],[],[],[]]
  for item in test_msgs:
#    for (dst_x,dst_y,payload,dir_out) in item:
    for i in range( len( item ) ):
      (dst_x,dst_y,payload,dir_out) = item[i]
      pkt = mk_pkt (0, 0, dst_x, dst_y, 1, payload)
      src_packets[dir_out].append( pkt )
      result_msgs[dir_out].append ( pkt )

  th = TestHarness( Packet, src_packets, result_msgs, 0, 0, 0, 0,
                    arrival_pipes )
  run_sim( th )
