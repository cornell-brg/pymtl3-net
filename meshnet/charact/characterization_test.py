#=========================================================================
# characterization_test.py
#=========================================================================
# Test for characterization
#
# Author : Cheng Tan
#   Date : June 10, 2019

from pymtl3                        import *
from ocn_pclib.ifcs.positions      import mk_mesh_pos
from ocn_pclib.ifcs.packets         import mk_mesh_pkt
from pymtl3.stdlib.test            import TestVectorSimulator
from meshnet.MeshRouterRTL        import MeshRouterRTL
from meshnet.DORYMeshRouteUnitRTL_wo_index import DORYMeshRouteUnitRTL
from router.SwitchUnitRTL_wo_index          import SwitchUnitRTL
from pymtl3.passes.sverilog import ImportPass, TranslationPass
from pymtl3.passes.sverilog.util.test_utility import closed_loop_component_input_test
from pymtl3.passes.CharacterizationPass import CharacterizationPass

#-------------------------------------------------------------------------
# characterization
#-------------------------------------------------------------------------

def test_characterization():

  def tv_in( model, test_vector ):

    MeshPos = mk_mesh_pos( 4, 4 )
    pkt = mk_mesh_pkt( 1, 1, 2, 2, 1, 0 )

    model.pos = MeshPos( 1, 1 )
    model.recv[4].msg = pkt
    model.recv[4].en  = 1

    for i in range (5):
      model.send[i].rdy = 1

#  def tv_out( model, test_vector ):
#    if test_vector[2] != 'x':
#      assert model.send[test_vector[2]].msg.payload == test_vector[3]

  test_vector = []

  mesh_wid = mesh_ht = 4
  MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )
  PacketType = mk_mesh_pkt( 4, 4, 1, 8, 32 )
  model = MeshRouterRTL( PacketType, MeshPos,
                         RouteUnitType = DORYMeshRouteUnitRTL, 
                         SwitchUnitType = SwitchUnitRTL )
#  model.elaborate()
#  model.sverilog_translate = True
#  model.apply( SimpleSim )
#  model.apply( TranslationPass() )
  model.apply( CharacterizationPass() )

#  closed_loop_component_input_test( model, test_vector, tv_in )
#  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )

