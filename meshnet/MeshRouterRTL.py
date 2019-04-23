#=========================================================================
# MeshRouteRTL.py
#=========================================================================
# Simple network-on-chip router, try to connect all the units together
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 8, 2019

from pymtl                import *
from router.Router        import Router
from router.InputUnitRTL  import InputUnitRTL
from router.SwitchUnitRTL import SwitchUnitRTL
from router.OutputUnitRTL import OutputUnitRTL

from DORYMeshRouteUnitRTL import DORYMeshRouteUnitRTL

class MeshRouterRTL( Router ):

  def construct( s, PacketType, PositionType, InputUnitType = InputUnitRTL,
                 RouteUnitType = DORYMeshRouteUnitRTL, 
                 SwitchUnitType = SwitchUnitRTL ):

    super( MeshRouterRTL, s ).construct(
      PacketType, PositionType, 5, 5, InputUnitType, RouteUnitType, 
      SwitchUnitType, OutputUnitRTL )
