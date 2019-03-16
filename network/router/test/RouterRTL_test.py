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
from network.router.RouterRTL      import RouterRTL
from network.router.RouteUnitRTL   import RouteUnitRTL

from network.routing.RoutingDORX   import RoutingDORX
from network.routing.RoutingDORY   import RoutingDORY

from ocn_pclib.Position import *

from Configs import configure_network

def run_test( model, test_vectors ):
 
  def tv_in( model, test_vector ):

    model.pos = MeshPosition( 5, 1, 1)
    for i in range (model.num_inports):
#    i = 0
      pkt = mk_pkt(0, 0, test_vector[0][i]/4, test_vector[0][i]%4, 
                   1, test_vector[3][i])
      model.recv[i].msg = pkt
      if model.recv[i].rdy == 1:
        model.recv[i].en = test_vector[1][i]

#    model.recv.rdy = 1
#    model.recv.en  = 1
    for i in range( model.num_outports ):
#      model.route_unit.send[i].rdy = 1
      model.send[i].rdy = test_vector[2][i]

  def tv_out( model, test_vector ):
    for i in range( model.num_inports ):
      assert model.recv[i].rdy == test_vector[4][i]

    for i in range (model.num_outports):
      assert model.send[i].en == (test_vector[5][i] != 'x')
      if model.send[i].en == 1:
        assert model.send[i].msg.payload == test_vector[5][i]
  
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()
  model.sim_reset()

def test_Router( dump_vcd, test_verilog ):

  configs = configure_network()

  if configs.routing_strategy == 'DORX':
    RoutingStrategyType = RoutingDORX
  elif configs.routing_strategy == 'DORY':
    RoutingStrategyType = RoutingDORY
  else:
    print 'Please specific a valid Routing strategy!'

  model = RouterRTL( 0, RoutingStrategyType, MeshPosition )

#  model.set_parameter("top.input_unit.queue.elaborate.num_entries", 4)
#  model.set_parameter("top.elaborate.num_outports", 5)
  xx = 'x'
  run_test( model, [
# [dst_x,dst_y]  recv_en    send_rdy       payload       recv_rdy      send_msg
  [[4,4,7,4,5],[1,1,0,1,1],[0,0,0,0,0],[11,12,13,14,15],[1,1,1,1,1],[xx,xx,xx,xx,xx]],
  [[4,4,7,8,9],[1,1,1,0,0],[0,0,0,0,0],[21,22,23,24,25],[0,0,1,0,1],[xx,xx,xx,xx,xx]],
  [[4,4,7,8,9],[1,1,1,1,1],[1,1,1,1,1],[31,32,33,34,35],[0,0,0,0,1],[11,23,xx,35,15]],
  [[4,6,7,8,9],[1,1,1,1,1],[1,1,1,1,1],[41,42,43,44,45],[1,1,1,0,1],[12,42,xx,45,xx]],
  [[9,0,0,4,6],[1,1,1,1,1],[1,1,0,1,1],[51,52,53,54,55],[1,1,1,0,1],[53,43,xx,51,xx]],
  ])

