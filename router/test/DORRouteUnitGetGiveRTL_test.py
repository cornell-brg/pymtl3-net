#=========================================================================
# DORYRouteUnitRTL_test.py
#=========================================================================
# Test for DORYRouteUnitRTL
#
# Author : Yanghui Ou, Cheng Tan
#   Date : Mar 25, 2019

from pymtl                          import *
from pclib.test                     import TestVectorSimulator
from ocn_pclib.ifcs.Packet          import Packet, mk_pkt
from ocn_pclib.ifcs.Position        import MeshPosition, mk_mesh_pos
from router.DORRouteUnitGetGiveRTL  import DORRouteUnitGetGiveRTL 

#-------------------------------------------------------------------------
# Driver function for TestVectorSimulator
#-------------------------------------------------------------------------

def run_test( model, router_pos, test_vectors ):
 
  def tv_in( model, test_vector ):

    dst_x   = test_vector[0]
    dst_y   = test_vector[1]
    opaque  = test_vector[2]
    payload = test_vector[3]

    pkt = mk_pkt( 0, 0, dst_x, dst_y, opaque, payload )

    model.pos = router_pos
    model.recv.msg = pkt
    model.recv.rdy = test_vector[5]

    for i in range( model.num_outports ):
      model.send[i].en = test_vector[7][i]

  def tv_out( model, test_vector ):

    assert model.recv.en == test_vector[4]
    for i in range( 5 ):
      assert model.send[i].rdy == test_vector[6][i]
      if test_vector[6][i]:
        assert model.send[i].msg.opaque  == test_vector[2]
        assert model.send[i].msg.payload == test_vector[3]
  
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

def test_route_unit( dump_vcd, test_verilog ):
  mesh_wid = 2
  mesh_ht  = 2

  MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )
  model = DORRouteUnitGetGiveRTL( Packet, MeshPos )

  # Test for Y-DOR routing algorithm

  run_test( model, MeshPos( 0, 0 ), [
   # dst_x  dst_y  opaque  payload get_en get_rdy   give_rdy       give_en 
   [   1,     1,     1,       9,      0,     1,    [0,1,0,0,0],  [0,0,0,0,0] ],
   [   0,     1,     1,       7,      0,     1,    [0,1,0,0,0],  [0,0,0,0,0] ],
   [   1,     0,     1,       3,      0,     1,    [0,0,0,1,0],  [0,0,0,0,0] ],
   [   0,     0,     1,       6,      0,     1,    [0,0,0,0,1],  [0,0,0,0,0] ],
   [   0,     0,     1,       4,      0,     0,    [0,0,0,0,0],  [0,0,0,0,0] ],
   [   0,     0,     1,       4,      1,     1,    [0,0,0,0,1],  [0,0,0,0,1] ],
  ] )

def test_route_unit3x3( dump_vcd, test_verilog ):
  mesh_wid = 3
  mesh_ht  = 3

  MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )
  model = DORRouteUnitGetGiveRTL( Packet, MeshPos )

  # Test for Y-DOR routing algorithm

  run_test( model, MeshPos( 0, 0 ), [
   # dst_x  dst_y  opaque  payload get_en get_rdy   give_rdy       give_en 
   [   1,     1,     1,       9,      0,     1,    [0,1,0,0,0],  [0,0,0,0,0] ],
   [   0,     1,     1,       7,      0,     1,    [0,1,0,0,0],  [0,0,0,0,0] ],
   [   1,     0,     1,       3,      0,     1,    [0,0,0,1,0],  [0,0,0,0,0] ],
   [   0,     0,     1,       6,      0,     1,    [0,0,0,0,1],  [0,0,0,0,0] ],
   [   0,     0,     1,       4,      0,     0,    [0,0,0,0,0],  [0,0,0,0,0] ],
   [   0,     0,     1,       4,      1,     1,    [0,0,0,0,1],  [0,0,0,0,1] ],
  ] )
