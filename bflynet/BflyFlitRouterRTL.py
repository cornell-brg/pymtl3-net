#=========================================================================
# BflyFlitRouteRTL.py
#=========================================================================
# Butterfly network-on-chip router (flit-based)
#
# Author : Cheng Tan
#   Date : July 19, 2019

from pymtl3 import *
from router.Router            import Router
from router.InputUnitRTL      import InputUnitRTL
from router.FlitSwitchUnitRTL import FlitSwitchUnitRTL
from router.OutputUnitRTL     import OutputUnitRTL
from DTRBflyRouteUnitRTL      import DTRBflyRouteUnitRTL
from DTRBflyFlitRouteUnitRTL  import DTRBflyFlitRouteUnitRTL

class BflyFlitRouterRTL( Router ):

  def construct( s, PacketType, PositionType, 
                 k_ary = 2, InputUnitType = InputUnitRTL, 
                 RouteUnitType = DTRBflyFlitRouteUnitRTL,
                 SwitchUnitType = FlitSwitchUnitRTL ):
    
    super( BflyFlitRouterRTL, s ).construct(
      PacketType, PositionType, k_ary, k_ary, InputUnitType, RouteUnitType,
      SwitchUnitType, OutputUnitRTL )

    for i in range( k_ary ):
      for j in range( k_ary ):
        s.connect( s.route_units[i].out_ocp[j], s.switch_units[j].out_ocp )
