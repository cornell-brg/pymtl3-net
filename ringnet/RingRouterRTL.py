#=========================================================================
# RingRouteRTL.py
#=========================================================================
# Ring network-on-chip router
#
# Author : Cheng Tan, Yanghui Ou
#   Date : April 6, 2019

from pymtl3 import *
from router.Router import Router
from router.SwitchUnitRTL import SwitchUnitRTL
from router.InputUnitCreditRTL import InputUnitCreditRTL
from router.OutputUnitCreditRTL import OutputUnitCreditRTL

from RingRouteUnitRTL import RingRouteUnitRTL

class RingRouterRTL( Router ):

  def construct( s,
    PacketType,
  	PositionType,
  	InputUnitType=InputUnitCreditRTL,
    RouteUnitType=RingRouteUnitRTL,
    SwitchUnitType=SwitchUnitRTL,
    OutputUnitType=OutputUnitCreditRTL
  ):

    super( RingRouterRTL, s ).construct(
      PacketType     = PacketType,
      PositionType   = PositionType,
      num_inports    = 3,
      num_outports   = 3,
      InputUnitType  = InputUnitType,
      RouteUnitType  = RouteUnitType,
      SwitchUnitType = SwitchUnitType,
      OutputUnitType = OutputUnitRTL
    )
