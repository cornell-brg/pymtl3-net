#=========================================================================
# MeshRouteRTL.py
#=========================================================================
# Simple network-on-chip router, try to connect all the units together
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 8, 2019

from pymtl3_net.cmeshnet.DORYCMeshRouteUnitRTL import DORYCMeshRouteUnitRTL
from pymtl3 import *
from pymtl3_net.router.InputUnitRTL import InputUnitRTL
from pymtl3_net.router.OutputUnitRTL import OutputUnitRTL
from pymtl3_net.router.Router import Router
from pymtl3_net.router.SwitchUnitRTL import SwitchUnitRTL


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
