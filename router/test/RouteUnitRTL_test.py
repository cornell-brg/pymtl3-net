#=========================================================================
# RouteUnitRTL_test.py
#=========================================================================
# Test for RouteUnitRTL
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 3, 2019

import tempfile
from pymtl                import *
from ocn_pclib.TestVectorSimulator            import TestVectorSimulator
from router.RouteUnitRTL  import RouteUnitRTL
from router.Packet import Packet, mk_pkt

from router.routing.RoutingDOR import RoutingDOR
from router.routing.RoutingWFR import RoutingWFR
from router.routing.RoutingNLR import RoutingNLR

import sys
from router.Configs import configure_network

def run_test( model, test_vectors ):
 
  def tv_in( model, test_vector ):
    pkt = mk_pkt( test_vector[0], test_vector[1], test_vector[2], test_vector[3],
            test_vector[4], test_vector[5])
    model.recv.msg = pkt
    model.recv.rdy = 1
    model.recv.en  = 1
    for i in range( model.num_outports ):
      model.send[i].rdy = 1

  def tv_out( model, test_vector ):
    assert 1 == 1
  
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

def test_RouteUnit( dump_vcd, test_verilog ):

  # pass the arguments/parameters and configure the module here
  print sys.argv[2:]
  configs = configure_network(sys.argv[2:])

  if configs.routing_strategy == 'DOR':
    routing = RoutingDOR
  elif configs.routing_strategy == 'WFR':
    routing = RoutingWFR
  elif configs.routing_strategy == 'NLR':
    routing = RoutingNLR
  else:
    print 'Please specific a valid routing strategy!'
    routing = RoutingDOR

  model = RouteUnitRTL( routing )

#  model.set_parameter("top.routing_logic.elaborate.dimension", 'y')
  model.set_parameter("top.elaborate.num_outports", 5)
  model.set_parameter("top.elaborate.pos_x", 1)
  model.set_parameter("top.elaborate.pos_y", 1)

  run_test( model, [
    #  src_x  src_y  dst_x  dst_y  opaque  payload  
   [     1,     1,     1,     1,     1,    0xdeadd00d  ],
   [     0,     0,     2,     2,     1,    0xdeadcafe  ],
   [     1,     0,     2,     1,     1,    0xdead0afe  ],
   [     0,     0,     1,     2,     1,    0x00000afe  ],
   [     2,     2,     0,     0,     1,    0x00000afe  ],
  ])
