#=========================================================================
# MeshFlitRouteRTL.py
#=========================================================================
# Flit-based CMesh router
#
# Author : Cheng Tan
#   Date : July 20, 2019

from pymtl3                             import *
from router.Router                      import Router
from router.InputUnitRTL                import InputUnitRTL
from router.SwitchUnitRTL               import SwitchUnitRTL
from router.FlitSwitchUnitRTL           import FlitSwitchUnitRTL
from router.OutputUnitRTL               import OutputUnitRTL
from cmeshnet.DORYCMeshFlitRouteUnitRTL import DORYCMeshFlitRouteUnitRTL

class CMeshFlitRouterRTL( Router ):

  def construct( s, PacketType, PositionType, num_inports, num_outports,
                 InputUnitType  = InputUnitRTL,
                 RouteUnitType  = DORYCMeshFlitRouteUnitRTL, 
                 SwitchUnitType = FlitSwitchUnitRTL ):

    super( CMeshFlitRouterRTL, s ).construct(
      PacketType, PositionType, num_inports, num_outports, 
      InputUnitType, RouteUnitType, SwitchUnitType, OutputUnitRTL )

    for i in range( num_inports ):
      for j in range( num_outports ):
        s.connect( s.route_units[i].out_ocp[j], s.switch_units[j].out_ocp )
