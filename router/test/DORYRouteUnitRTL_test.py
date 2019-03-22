#=========================================================================
# DORYRouteUnitRTL_test.py
#=========================================================================
# Test for DORYRouteUnitRTL
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 3, 2019

import tempfile
from pymtl                import *
from ocn_pclib.test.TestVectorSimulator            import TestVectorSimulator
from ocn_pclib.ifcs.Packet import Packet, mk_pkt
from router.DORYRouteUnitRTL  import DORYRouteUnitRTL

from ocn_pclib.ifcs.Position import *

from Configs import configure_network

def run_test( model, test_vectors ):
 
  def tv_in( model, test_vector ):

    # assume a 2x2 Mesh network
    pos = MeshPosition( 3, 1, 1)
    model.pos = pos

    pkt = mk_pkt(0, 0, test_vector[0], test_vector[1], test_vector[2], test_vector[3])
    model.recv.msg = pkt

    for i in range( model.num_outports ):
      model.send[i].rdy = test_vector[4][i]
      if test_vector[4][test_vector[5]] == 1:
        model.recv.en = 1


  def tv_out( model, test_vector ):
    assert model.recv.rdy == test_vector[4][test_vector[5]]
    if test_vector[4][test_vector[5]] == 1:
      assert model.send[test_vector[5]].en == 1
      assert model.send[test_vector[5]].msg.payload == test_vector[3]
  
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()
  model.sim_reset()

def test_RouteUnit( dump_vcd, test_verilog ):

  configs = configure_network()

  model = DORYRouteUnitRTL( Packet, MeshPosition )

  model.set_parameter("top.elaborate.num_outports", 5)

  # specific for DOR Y routing algorithm
  run_test( model, [
    #  dst_x  dst_y  opaque  payload      rdy       dir
   [     1,     1,     1,       9,    [0,0,0,0,1],   4  ],
   [     2,     2,     1,       7,    [1,0,0,0,0],   1  ],
   [     2,     1,     1,       3,    [0,0,1,0,0],   3  ],
   [     1,     2,     1,       6,    [0,1,0,1,0],   1  ],
   [     0,     0,     1,       4,    [1,0,0,0,0],   0  ],
  ])
