#=========================================================================
# RingRouteRTL.py
#=========================================================================
# Ring network-on-chip router
#
# Author : Cheng Tan, Yanghui Ou
#   Date : April 6, 2019

from pymtl import *
from router.Router        import Router
from router.InputUnitRTL  import InputUnitRTL
from router.SwitchUnitRTL import SwitchUnitRTL
from router.OutputUnitRTL import OutputUnitRTL

from RingRouteUnitRTL     import RingRouteUnitRTL

class RingRouterRTL( Router ):

  def construct( s, PacketType, PositionType, InputUnitType = InputUnitRTL,
                 RouteUnitType = RingRouteUnitRTL,
                 SwitchUnitType = SwitchUnitRTL ):
    
    super( RingRouterRTL, s ).construct(
      PacketType, PositionType, 3, 3, InputUnitType, RouteUnitType, 
      SwitchUnitType, OutputUnitRTL )
