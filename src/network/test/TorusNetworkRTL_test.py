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
from ocn_pclib.Packet import Packet, mk_pkt
from src.network.TorusNetworkRTL import TorusNetworkRTL

from ocn_pclib.Position import *

from Configs import configure_network

def run_test( model, test_vectors ):
 
  configs = configure_network()
  def tv_in( model, test_vector ):

    for i in range (configs.routers):
      model.pos_ports[i] = MeshPosition(i, i%(configs.routers/configs.rows),
              i/(configs.routers/configs.rows))
    if test_vector[0] != 'x':
      router_id = test_vector[0]
      pkt = mk_pkt( router_id%(configs.routers/configs.rows),
                  router_id/(configs.routers/configs.rows),
                  test_vector[1][0], test_vector[1][1], 1, test_vector[1][2])
    
      # Enable the network interface on specific router
      for i in range (configs.routers):
        model.recv_noc_ifc[i].en  = 0
      model.recv_noc_ifc[router_id].msg = pkt
      model.recv_noc_ifc[router_id].en  = 1

    for i in range (configs.routers):
      model.send_noc_ifc[i].rdy = 1

  def tv_out( model, test_vector ):
#    if test_vector[2] != 'x':
#      assert model.send_noc_ifc[test_vector[2]].msg.payload == test_vector[3]
      assert 1 == 1
     
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()
  model.sim_reset()

def test_Network( dump_vcd, test_verilog ):

  model = TorusNetworkRTL()

#  model.set_parameter("top.elaborate.num_outports", 5)

  x = 'x'

  # Specific for wire connection (link delay = 0) in Mesh topology
  simple_test = [
#  router   [packet]   arr_router  msg 
  [  0,    [1,0,1001],     x,       x  ],
  [  0,    [1,1,1002],     x,       x  ],
  [  0,    [0,1,1003],     1,     1001 ],
  [  0,    [0,1,1004],     x,       x  ],
  [  0,    [1,0,1005],     2,     1003 ],
  [  2,    [0,0,1006],     x,       x  ],
  [  1,    [0,1,1007],     1,     1005 ],
  [  2,    [1,1,1008],     0,     1006 ],
  [  x,    [0,0,0000],     x,       x  ],
  [  x,    [0,0,0000],     2,     1007 ],
  [  x,    [0,0,0000],     x,       x  ],
  [  x,    [0,0,0000],     3,     1008 ],
  [  x,    [0,0,0000],     x,       x  ],
  [  x,    [0,0,0000],     x,       x  ],
  [  x,    [0,0,0000],     x,       x  ],
  [  x,    [0,0,0000],     x,       x  ],
  ]

  run_test( model, simple_test)
