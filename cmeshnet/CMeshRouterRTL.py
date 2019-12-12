#=========================================================================
# MeshRouteRTL.py
#=========================================================================
# Simple network-on-chip router, try to connect all the units together
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 8, 2019

from cmeshnet.DORYCMeshRouteUnitRTL import DORYCMeshRouteUnitRTL
from pymtl3 import *
from router.InputUnitRTL import InputUnitRTL
from router.OutputUnitRTL import OutputUnitRTL
from router.Router import Router
from router.SwitchUnitRTL import SwitchUnitRTL


class CMeshRouterRTL( Router ):

  def construct( s, PacketType, PositionType, num_inports, num_outports,
                 InputUnitType  = InputUnitRTL,
                 RouteUnitType  = DORYCMeshRouteUnitRTL,
                 SwitchUnitType = SwitchUnitRTL ):

    super().construct(
      PacketType,
      PositionType,
      num_inports,
      num_outports,
      InputUnitType,
      RouteUnitType,
      SwitchUnitType,
      OutputUnitRTL,
    )
