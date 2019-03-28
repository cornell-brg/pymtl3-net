#=========================================================================
# RouterRTL_test.py
#=========================================================================
# Test for RouterRTL
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 10, 2019

import tempfile
from pymtl                   import *
from router.RouterRTL        import MeshRouterRTL
from router.InputUnitRTL     import InputUnitRTL
from router.DORXRouteUnitRTL import DORXRouteUnitRTL
from router.DORYRouteUnitRTL import DORYRouteUnitRTL
from router.SwitchUnitRTL    import SwitchUnitRTL
from router.OutputUnitRTL    import OutputUnitRTL
from ocn_pclib.rtl.queues    import NormalQueueRTL

from ocn_pclib.ifcs.Position import *
from ocn_pclib.ifcs.Packet   import Packet, mk_pkt
from pclib.test import TestVectorSimulator

from Configs import configure_network

def run_test( model, test_vectors ):
 
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

def test_Router( dump_vcd, test_verilog ):

  configs = configure_network()

  if configs.routing_strategy == 'DORX':
    RouteUnitType = DORXRouteUnitRTL
  elif configs.routing_strategy == 'DORY':
    RouteUnitType = DORYRouteUnitRTL
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

  model = MeshRouterRTL( Packet, MeshPosition, RouteUnitType )
#  for i in range ( 5 ):
#    queue_path = "top.input_units[" + str(i) + "].elaborate.QueueType"
#    model.set_parameter( queue_path, NormalQueueRTL )

  run_test(model, inputs_buffer)

