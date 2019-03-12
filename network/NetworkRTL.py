#=========================================================================
# NetworkRTL.py
#=========================================================================
# Simple network implementation.
#
# Author : Cheng Tan
#   Date : Mar 10, 2019

from pymtl import *
from pclib.ifcs.EnRdyIfc  import InEnRdyIfc, OutEnRdyIfc

from network.router.MeshRouteUnitRTL  import MeshRouteUnitRTL

class NetworkRTL( RTLComponent ):
  def construct( s, RouterType, RoutingStrategyType, TopologyType ):

    pos = MeshPosition( 2, 1, 1)
    RouteUnitType = MeshRouteUnitRTL

    RouterType( RoutingStrategyType, RouteUnitType )

    # Interface
    s.recv = InEnRdyIfc( Packet )
    s.send = [ OutEnRdyIfc (Packet) for _ in range ( s.num_outports ) ]

    # Components
