#=========================================================================
# RouteUnitWithRoutingRTL_test.py
#=========================================================================
# Test for RouteUnitWithRoutingRTL
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 3, 2019

import tempfile
from pymtl                import *
from ocn_pclib.TestVectorSimulator            import TestVectorSimulator
from ocn_pclib.Packet import Packet, mk_pkt
from network.router.RouteUnitRTL  import RouteUnitRTL

from network.routing.RoutingDORX import RoutingDORX
from network.routing.RoutingDORY import RoutingDORY

from ocn_pclib.Position import *

from Configs import configure_network

def run_test( model, test_vectors ):
 
  def tv_in( model, test_vector ):

    pos = MeshPosition( 3, 1, 1)
    model.pos = pos

    pkt = mk_pkt( test_vector[0], test_vector[1], test_vector[2], test_vector[3],
            test_vector[4], test_vector[5])
    model.recv.msg = pkt
    model.recv.en  = model.recv.rdy
#    model.recv.en  = 1
    for i in range( model.num_outports ):
      model.send[i].rdy = test_vector[6][i]

  def tv_out( model, test_vector ):
    assert model.send[test_vector[7]].en == test_vector[6][test_vector[7]]
    # msg assert
    # recv rdy
    # send en
  
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()
  model.sim_reset()

def test_RouteUnit( dump_vcd, test_verilog ):

  configs = configure_network()

  if configs.routing_strategy == 'DORX':
    Routing = RoutingDORX
  elif configs.routing_strategy == 'DORY':
    Routing = RoutingDORY
  else:
    print 'Please specific a valid Routing strategy!'

  routing_logic = Routing( Packet )
  model = RouteUnitRTL( routing_logic, MeshPosition )

  model.set_parameter("top.elaborate.num_outports", 5)

  # specific for DOR Y routing algorithm
  run_test( model, [
    #  src_x  src_y  dst_x  dst_y  opaque  payload      rdy      dir
   [     1,     1,     1,     1,     1,       9,    [0,0,0,0,1],  4  ],
   [     0,     0,     2,     2,     1,       7,    [1,0,0,0,0],  1  ],
   [     1,     0,     2,     1,     1,       3,    [0,0,1,0,0],  3  ],
   [     0,     0,     1,     2,     1,       6,    [0,1,0,1,0],  1  ],
   [     2,     2,     0,     0,     1,       4,    [1,0,0,0,0],  0  ],
  ])
