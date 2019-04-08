#=========================================================================
# ButterflyRouteRTL.py
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

class ButterflyRouterRTL( Router ):

  def construct( s, PacketType, PositionType, RouteUnitType, k_ary ):
    
    super( ButterflyRouterRTL, s ).construct(
      PacketType, PositionType, k_ary, k_ary, InputUnitRTL, RouteUnitType, 
      SwitchUnitRTL, OutputUnitRTL )
