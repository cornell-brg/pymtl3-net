#=========================================================================
# MeshNetworkRTL_test.py
#=========================================================================
# Test for MeshNetworkRTL
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 20, 2019

import tempfile
from pymtl                import *
from network.MeshNetworkRTL import MeshNetworkRTL

from ocn_pclib.rtl.queues  import NormalQueueRTL

from pclib.test import TestVectorSimulator
from ocn_pclib.ifcs.Packet              import Packet, mk_pkt
from ocn_pclib.ifcs.Position            import *

from Configs import configure_network

def run_test( model, test_vectors ):
 
  configs = configure_network()
  def tv_in( model, test_vector ):

    mesh_wid = 4
    mesh_ht  = 4
    MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )

    for i in range (configs.routers):
      model.pos_ports[i] = MeshPos( i%(configs.routers/configs.rows), i/(configs.routers/configs.rows) )
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
    if test_vector[2] != 'x':
      assert model.send_noc_ifc[test_vector[2]].msg.payload == test_vector[3]
#      assert 1 == 1
     
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()
  model.sim_reset()

def test_MeshNetwork( dump_vcd, test_verilog ):

  configs = configure_network()
  model = MeshNetworkRTL()

  num_routers = configs.routers
  num_inports = configs.router_inports
  for r in range (num_routers):
    for i in range (num_inports):
      path = "top.routers[" + str(r) + "].input_units[" + str(i) + "].elaborate.QueueType"
      model.set_parameter(path, NormalQueueRTL)

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
