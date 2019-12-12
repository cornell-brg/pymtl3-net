"""
=========================================================================
BfRouteRTL.py
=========================================================================
RTL router for butterfly network.

Author : Cheng Tan, Yanghui Ou
  Date : April 6, 2019
"""
from pymtl3 import *
from router.InputUnitRTL import InputUnitRTL
from router.OutputUnitRTL import OutputUnitRTL
from router.Router import Router
from router.SwitchUnitRTL import SwitchUnitRTL

from .DTRBflyRouteUnitRTL import DTRBflyRouteUnitRTL


class BflyRouterRTL( Router ):

  def construct( s,
    PacketType,
    PositionType,
    k_ary = 2,
    InputUnitType = InputUnitRTL,
    RouteUnitType = DTRBflyRouteUnitRTL,
    SwitchUnitType = SwitchUnitRTL
  ):

    super().construct(
      PacketType,
      PositionType,
      k_ary,
      k_ary,
      InputUnitType,
      RouteUnitType,
      SwitchUnitType,
      OutputUnitRTL,
    )
