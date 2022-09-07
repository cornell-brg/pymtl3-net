"""
=========================================================================
MeshRouteRTL.py
=========================================================================
Simple network-on-chip router, try to connect all the units together

Author : Cheng Tan, Yanghui Ou
  Date : Mar 8, 2019
"""
from pymtl3 import *
from pymtl3_net.router.InputUnitRTL import InputUnitRTL
from pymtl3_net.router.OutputUnitRTL import OutputUnitRTL
from pymtl3_net.router.Router import Router
from pymtl3_net.router.SwitchUnitRTL import SwitchUnitRTL

from .DORYMeshRouteUnitRTL import DORYMeshRouteUnitRTL


class MeshRouterRTL( Router ):

  def construct( s, PacketType, PositionType, InputUnitType = InputUnitRTL,
                 RouteUnitType = DORYMeshRouteUnitRTL,
                 SwitchUnitType = SwitchUnitRTL ):

    super().construct(
      PacketType, PositionType, 5, 5, InputUnitType, RouteUnitType,
      SwitchUnitType, OutputUnitRTL )
