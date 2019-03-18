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
from network.NetworkRTL import NetworkRTL

from ocn_pclib.Position import *

from Configs import configure_network

def run_test( model, test_vectors ):
 
  configs = configure_network()
#  positions = mk_mesh_pos( configs.rows, configs.routers )
  def tv_in( model, test_vector ):

    for i in range( configs.routers ):
      model.pos_ports[i] = MeshPosition(i, i%(configs.routers/configs.rows),
              i/(configs.routers/configs.rows))
      model.routers[i].send[4].rdy = 1
      model.routers[i].recv[4].en  = 1
    router_id = test_vector[0]
    pkt = mk_pkt( router_id%(configs.routers/configs.rows),
                  router_id/(configs.routers/configs.rows),
                  test_vector[1][0], test_vector[1][1], 1, test_vector[1][2])
    
    # Enable the network interface on specific router
    model.recv_noc_ifc[router_id].msg = pkt
    model.recv_noc_ifc[router_id].en  = 1
    model.send_noc_ifc[router_id].rdy  = 1

  def tv_out( model, test_vector ):
    if test_vector[2] != 'x':
      print model.send_noc_ifc[test_vector[2]].msg.payload
    assert 1 == 1
     
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()
  model.sim_reset()

def test_Network( dump_vcd, test_verilog ):

  model = NetworkRTL()

#  model.set_parameter("top.elaborate.num_outports", 5)

  x = 'x'
  simple_test = [
#  router   [packet]   arr_router  msg 
  [  0,    [1,0,1001],     x,       x  ],
  [  0,    [1,1,1002],     x,       x  ],
  [  0,    [0,1,1003],     2,       x  ],
  [  0,    [0,1,1004],     2,     1002 ],
  [  0,    [1,0,1005],     1,     1001 ], ##
  [  2,    [0,0,1006],     2,     1003 ],
  [  1,    [1,1,1007],     2,     1003 ], ##
  [  2,    [1,1,1008],     2,     1003 ],
  [  0,    [0,0,0000],     3,      0  ],
  [  0,    [0,0,0000],     3,     1007 ],
  [  0,    [0,0,0000],     3,     1007 ], ##
  [  0,    [0,0,0000],     3,      0  ],
  [  0,    [0,0,0000],     3,      0  ],
  [  0,    [0,0,0000],     3,      0  ],
  [  0,    [0,0,0000],     3,      0  ],
  [  0,    [0,0,0000],     3,      0  ],
  ]

  run_test( model, simple_test)
