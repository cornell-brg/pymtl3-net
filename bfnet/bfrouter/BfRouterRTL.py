#=========================================================================
# BfRouteRTL.py
#=========================================================================
# Butterfly network-on-chip router
#
# Author : Cheng Tan, Yanghui Ou
#   Date : April 6, 2019

from pymtl import *
from router.Router        import Router
from router.InputUnitRTL  import InputUnitRTL
from router.SwitchUnitRTL import SwitchUnitRTL
from router.OutputUnitRTL import OutputUnitRTL
from DTRBfRouteUnitRTL    import DTRBfRouteUnitRTL

class BfRouterRTL( Router ):

  def construct( s, PacketType, PositionType, 
                 k_ary = 2, InputUnitType = InputUnitRTL, 
                 RouteUnitType = DTRBfRouteUnitRTL,
                 SwitchUnitType = SwitchUnitRTL ):
    
    super( BfRouterRTL, s ).construct(
      PacketType, PositionType, k_ary, k_ary, InputUnitType, RouteUnitType,
      SwitchUnitType, OutputUnitRTL )
