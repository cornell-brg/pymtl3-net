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

    model.pos = MeshPosition( 3, 1, 1)
    pkts = []
    for i in range (5):
#    i = 0
      pkts.append(mk_pkt( (test_vector[0]+i)%4, (test_vector[1]+i)%4, 
                          (test_vector[2]+i)%4, (test_vector[3]+i)%4, 
                          (test_vector[4]+i)%4, (test_vector[5]+i)%4 ))

    for i in range (5):
      model.recv[i].msg = pkts[i]
      if model.recv[i].rdy == 1:
        model.recv[i].en = 1

#    model.recv.rdy = 1
#    model.recv.en  = 1
    for i in range( model.num_outports ):
#      model.route_unit.send[i].rdy = 1
      model.send[i].rdy = 1

  def tv_out( model, test_vector ):
    assert 1 == 1
  
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

  run_test( model, [
    #  src_x  src_y  dst_x  dst_y  opaque  payload  
   [     1,     1,     1,     1,     1,    0xdeadd00d  ],
   [     0,     0,     2,     2,     1,    0xdeadcafe  ],
   [     1,     0,     2,     1,     1,    0xdead0afe  ],
   [     0,     0,     1,     2,     1,    0x00000afe  ],
   [     2,     2,     0,     0,     1,    0x00000afe  ],
  ])
