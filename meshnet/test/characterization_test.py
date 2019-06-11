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
from meshnet.DORYMeshRouteUnitRTL import DORYMeshRouteUnitRTL
from router.ULVCUnitRTL           import ULVCUnitRTL
from router.InputUnitRTL          import InputUnitRTL

from test_helpers import dor_routing

from pymtl3.passes.sverilog import ImportPass, TranslationPass

#-------------------------------------------------------------------------
# characterization
#-------------------------------------------------------------------------

def test_characterization():

  mesh_wid = mesh_ht = 4
  MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )
  model = MeshRouterRTL( Packet, MeshPos, InputUnitType = InputUnitRTL, RouteUnitType = DORYMeshRouteUnitRTL )
  model.elaborate()
  model.sverilog_translate = True
#  model.apply( SimpleSim )
  model.apply( TranslationPass() )

