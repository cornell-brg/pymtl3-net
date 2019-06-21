#=========================================================================
# MeshNetworkRTL_test.py
#=========================================================================
# Test for NetworkRTL
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 20, 2019

from pymtl3                        import *
from pymtl3.stdlib.rtl.queues      import NormalQueueRTL
from pymtl3.stdlib.test.test_srcs  import TestSrcRTL
from ocn_pclib.test.net_sinks      import TestNetSinkRTL
#from pymtl3.stdlib.test.test_sinks import TestSinkRTL
from pymtl3.stdlib.test            import TestVectorSimulator
#from ocn_pclib.ifcs.Packet         import Packet, mk_pkt
#from ocn_pclib.ifcs.Position       import *
# from ocn_pclib.draw               import *
from meshnet.MeshNetworkRTL        import MeshNetworkRTL
from meshnet.DORYMeshRouteUnitRTL  import DORYMeshRouteUnitRTL
from meshnet.DORXMeshRouteUnitRTL  import DORXMeshRouteUnitRTL
from meshnet.TestMeshRouteUnitRTL  import TestMeshRouteUnitRTL
from router.InputUnitRTL           import InputUnitRTL

from ocn_pclib.ifcs.positions      import mk_mesh_pos
from ocn_pclib.ifcs.packets        import mk_mesh_pkt

from pymtl3.passes.sverilog import ImportPass, TranslationPass
from pymtl3.passes import DynamicSim

#-------------------------------------------------------------------------
# Test Vector
#-------------------------------------------------------------------------
def run_vector_test( model, test_vectors, mesh_wid, mesh_ht ):
 
  def tv_in( model, test_vector ):
    num_routers = mesh_wid * mesh_ht
    MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )
    PacketType = mk_mesh_pkt( mesh_wid, mesh_ht )

    if test_vector[0] != 'x':
      router_id = test_vector[0]
      pkt = PacketType( router_id % mesh_wid, router_id / mesh_wid,
                  test_vector[1][0], test_vector[1][1], 1, test_vector[1][2])
    
      # Enable the network interface on specific router
      for i in range (num_routers):
        model.recv[i].en  = 0
      model.recv[router_id].msg = pkt
      model.recv[router_id].en  = 1

    XYType = mk_bits( clog2( mesh_wid ) )
    for i in range (num_routers):
      model.send[i].rdy = 1
      model.pos_x[i] = XYType(i%mesh_wid)
      model.pos_y[i] = XYType(i/mesh_wid)

  def tv_out( model, test_vector ):
    if test_vector[2] != 'x':
      assert model.send[test_vector[2]].msg.payload == test_vector[3]
     
  model.elaborate()
  model.sverilog_translate = True
  model.sverilog_import = True
  model.apply( TranslationPass() )
  model = ImportPass()( model )
#  model.apply( SimpleSim )
#  model.apply( DynamicSim )
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

def test_vector_mesh2x1( dump_vcd, test_verilog ):

  mesh_wid = 2
  mesh_ht  = 1
  MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )
  num_routers = mesh_wid * mesh_ht 
  num_inports = 5
  PacketType = mk_mesh_pkt( mesh_wid, mesh_ht )
  model = MeshNetworkRTL( PacketType, MeshPos, mesh_wid, mesh_ht, 0 )

  x = 'x'

  # Specific for wire connection (link delay = 0) in 2x2 Mesh topology
  simple_2_2_test = [
#  router   [packet]   arr_router  msg 
  [  0,    [1,0,1001],     x,       x  ],
  [  1,    [0,0,1002],     x,       x  ],
  [  0,    [1,0,1003],     1,     1001 ],
  [  1,    [0,0,1004],     x,       x  ],
  [  0,    [1,0,1005],     1,     1003 ],
  [  1,    [0,0,1006],     x,       x  ],
  [  1,    [0,0,1007],     1,     1005 ],
  [  0,    [1,0,1008],     0,     1006 ],
  [  x,    [0,0,0000],     0,     1007  ],
  [  x,    [0,0,0000],     1,     1008 ],
  ]

  model.set_param("top.routers*.construct", RouteUnitType=DORYMeshRouteUnitRTL)

  run_vector_test( model, simple_2_2_test, mesh_wid, mesh_ht)

