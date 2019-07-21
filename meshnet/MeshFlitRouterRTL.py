#=========================================================================
# MeshFlitRouteRTL.py
#=========================================================================
# Flit-based Mesh router
#
# Author : Cheng Tan
#   Date : July 20, 2019

from pymtl3                   import *
from router.Router            import Router
from router.InputUnitRTL      import InputUnitRTL
from router.SwitchUnitRTL     import SwitchUnitRTL
from router.FlitSwitchUnitRTL import FlitSwitchUnitRTL
from router.OutputUnitRTL     import OutputUnitRTL
from DORYMeshRouteUnitRTL     import DORYMeshRouteUnitRTL
from TestMeshRouteUnitRTL     import TestMeshRouteUnitRTL

class MeshFlitRouterRTL( Router ):

  def construct( s, PacketType, PositionType, InputUnitType = InputUnitRTL,
                 RouteUnitType = DORYMeshRouteUnitRTL,
                 SwitchUnitType = FlitSwitchUnitRTL ):

    super( MeshFlitRouterRTL, s ).construct(
      PacketType, PositionType, 5, 5, InputUnitType, RouteUnitType, 
      SwitchUnitType, OutputUnitRTL )

    for i in range( 5 ):
      for j in range( 5 ):
        s.connect( s.route_units[i].out_ocp[j], s.switch_units[j].out_ocp )
