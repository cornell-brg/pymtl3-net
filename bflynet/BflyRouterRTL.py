#=========================================================================
# BfRouteRTL.py
#=========================================================================
# Butterfly network-on-chip router
#
# Author : Cheng Tan, Yanghui Ou
#   Date : April 6, 2019

from pymtl3 import *
from router.Router        import Router
from router.InputUnitRTL  import InputUnitRTL
from router.SwitchUnitRTL import SwitchUnitRTL
from router.OutputUnitRTL import OutputUnitRTL
from DTRBflyRouteUnitRTL  import DTRBflyRouteUnitRTL

class BflyRouterRTL( Router ):

  def construct( s, PacketType, PositionType, 
                 k_ary = 2, InputUnitType = InputUnitRTL, 
                 RouteUnitType = DTRBflyRouteUnitRTL,
                 SwitchUnitType = SwitchUnitRTL ):
    
    super( BflyRouterRTL, s ).construct(
      PacketType, PositionType, k_ary, k_ary, InputUnitType, RouteUnitType,
      SwitchUnitType, OutputUnitRTL )
