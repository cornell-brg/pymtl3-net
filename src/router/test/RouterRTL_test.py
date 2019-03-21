#=========================================================================
# RouterRTL_test.py
#=========================================================================
# Test for RouterRTL
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 10, 2019

import tempfile
from pymtl                         import *
from ocn_pclib.TestVectorSimulator import TestVectorSimulator
from ocn_pclib.Packet              import Packet, mk_pkt
from src.router.RouterRTL      import RouterRTL
from src.router.DORXRouteUnitRTL   import DORXRouteUnitRTL
from src.router.DORYRouteUnitRTL   import DORYRouteUnitRTL

from ocn_pclib.Position import *

from pclib.rtl  import NormalQueueRTL
from pclib.rtl  import BypassQueue1RTL

from Configs import configure_network

def run_test( model, test_vectors ):
 
  def tv_in( model, test_vector ):

    model.pos = MeshPosition( 5, 1, 1)
    for i in range (model.num_inports):
      pkt = mk_pkt(0, 0, test_vector[0][i]/4, test_vector[0][i]%4, 
                   1, test_vector[3][i])
      model.recv[i].msg = pkt
      if model.recv[i].rdy == 1:
        model.recv[i].en = test_vector[1][i]

    for i in range( model.num_outports ):
      model.send[i].rdy = test_vector[2][i]

  def tv_out( model, test_vector ):
    for i in range( model.num_inports ):
#      print 'model.recv[',i,'].rdy:',model.recv[i].rdy,' == test_vector[4][',i,']:',test_vector[4][i]
      assert model.recv[i].rdy == test_vector[4][i]

    for i in range (model.num_outports):
#      print 'model.send[',i,'].en:',model.send[i].en,' == (test_vector[5][',i,']:',test_vector[5][i]
      assert model.send[i].en == (test_vector[5][i] != 'x')
      if model.send[i].en == 1:
#        print '  model.send[',i,'].msg.payload:',model.send[i].msg.payload,' == test_vector[5][',i,']:',test_vector[5][i]
        assert model.send[i].msg.payload == test_vector[5][i]
  
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()
  model.sim_reset()

def test_Router( dump_vcd, test_verilog ):

  configs = configure_network()

  if configs.routing_strategy == 'DORX':
    RouteUnitType = DORXRouteUnitRTL
  elif configs.routing_strategy == 'DORY':
    RouteUnitType = DORYRouteUnitRTL
  else:
    print 'Please specific a valid Routing strategy!'

  xx = 'x'
  inputs_0_buffer= [
# [dst_x,dst_y]  recv_en    send_rdy       payload       recv_rdy      send_msg
  [[4,4,7,4,5],[1,1,0,1,1],[0,0,0,0,0],[11,12,13,14,15],[1,1,1,1,1],[xx,xx,xx,xx,xx]],
  [[4,4,7,8,9],[1,1,1,0,0],[0,0,0,0,0],[21,22,23,24,25],[0,0,1,0,1],[xx,xx,xx,xx,xx]],
  [[4,4,7,8,9],[1,1,1,1,1],[1,1,1,1,1],[31,32,33,34,35],[0,0,0,0,1],[11,23,xx,35,15]],
  [[4,6,7,8,9],[1,1,1,1,1],[1,1,1,1,1],[41,42,43,44,45],[1,1,1,0,1],[12,42,xx,45,xx]],
  [[9,0,0,4,6],[1,1,1,1,1],[1,1,0,1,1],[51,52,53,54,55],[1,1,1,0,1],[53,43,xx,51,xx]],
  ]

  inputs_1_buffer= [
# [dst_x,dst_y]  recv_en    send_rdy       payload       recv_rdy      send_msg
  [[4,4,7,4,5],[1,1,0,1,1],[0,0,0,0,0],[11,12,13,14,15],[1,1,1,1,1],[xx,xx,xx,xx,xx]],
  [[4,4,7,8,9],[1,1,1,0,0],[0,0,0,0,0],[21,22,23,24,25],[0,0,1,0,0],[xx,xx,xx,xx,xx]],
  [[4,4,7,8,9],[1,1,1,1,1],[1,1,1,1,1],[31,32,33,34,35],[1,1,0,1,1],[11,23,xx,xx,15]],
  [[4,6,7,8,9],[1,1,1,1,1],[1,1,1,1,1],[41,42,43,44,45],[0,0,1,1,1],[12,xx,xx,xx,xx]],
  [[9,0,0,4,6],[1,1,1,1,1],[1,1,0,1,1],[51,52,53,54,55],[1,0,0,0,0],[14,43,xx,45,xx]],
  ]


#  model = RouterRTL( 0, RoutingStrategyType, MeshPosition, NormalQueueRTL )
#  run_test(model, inputs_1_buffer)

  model = RouterRTL( RouteUnitType, MeshPosition )
  run_test(model, inputs_0_buffer)



