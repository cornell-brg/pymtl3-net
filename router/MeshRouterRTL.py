#=========================================================================
# RouteRTL.py
#=========================================================================
# Simple network-on-chip router, try to connect all the units together
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 8, 2019

from pymtl import *
from router.Router        import Router
from router.InputUnitRTL  import InputUnitRTL
from router.SwitchUnitRTL import SwitchUnitRTL
from router.OutputUnitRTL import OutputUnitRTL

class MeshRouterRTL( Router ):

  def construct( s, PacketType, PositionType, RouteUnitType ):
    
    super( MeshRouterRTL, s ).construct(
      PacketType, PositionType, 5, 5, InputUnitRTL, RouteUnitType, 
      SwitchUnitRTL, OutputUnitRTL )