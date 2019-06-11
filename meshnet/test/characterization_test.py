#=========================================================================
# characterization_test.py
#=========================================================================
# Test for characterization
#
# Author : Cheng Tan
#   Date : June 10, 2019

import hypothesis
from hypothesis import strategies as st

from pymtl3                        import *
from pymtl3.stdlib.test.test_srcs  import TestSrcRTL
from ocn_pclib.test.net_sinks      import TestNetSinkRTL
from ocn_pclib.ifcs.positions      import mk_mesh_pos
from ocn_pclib.ifcs.Packet         import Packet, mk_pkt 
from pymtl3.stdlib.test            import TestVectorSimulator
from meshnet.MeshRouterRTL        import MeshRouterRTL
from meshnet.DORXMeshRouteUnitRTL import DORXMeshRouteUnitRTL
#from meshnet.DORYMeshRouteUnitRTL import DORYMeshRouteUnitRTL
from meshnet.DORYMeshRouteUnitRTL_wo_index import DORYMeshRouteUnitRTL
from router.ULVCUnitRTL           import ULVCUnitRTL
from router.InputUnitRTL          import InputUnitRTL
from router.SwitchUnitRTL_wo_index          import SwitchUnitRTL

from test_helpers import dor_routing

from pymtl3.passes.sverilog import ImportPass, TranslationPass
from pymtl3.passes.sverilog.util.test_utility import closed_loop_component_input_test

#-------------------------------------------------------------------------
# characterization
#-------------------------------------------------------------------------

def test_characterization():

  def tv_in( model, test_vector ):

    MeshPos = mk_mesh_pos( 9, 9 )
    pkt = mk_pkt( 1, 1, 2, 2, 1, 0 )

    model.pos = MeshPos( 1, 1 )
    model.recv[4].msg = pkt
    model.recv[4].en  = 1

    for i in range (5):
      model.send[i].rdy = 1

#  def tv_out( model, test_vector ):
#    if test_vector[2] != 'x':
#      assert model.send[test_vector[2]].msg.payload == test_vector[3]

  test_vector = []

  mesh_wid = mesh_ht = 9
  MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )
  model = MeshRouterRTL( Packet, MeshPos, InputUnitType = InputUnitRTL, 
          RouteUnitType = DORYMeshRouteUnitRTL, SwitchUnitType = SwitchUnitRTL )
#  model.elaborate()
#  model.sverilog_translate = True
#  model.apply( SimpleSim )
#  model.apply( TranslationPass() )

  closed_loop_component_input_test( model, test_vector, tv_in )

#  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )

