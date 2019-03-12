#=========================================================================
# NetworkRTL.py
#=========================================================================
# Simple network implementation.
#
# Author : Cheng Tan
#   Date : Mar 10, 2019

from pymtl                        import *
from pclib.ifcs.EnRdyIfc          import InEnRdyIfc, OutEnRdyIfc

from network.router.RouteUnitRTL  import RouteUnitRTL
from network.router.RouterRTL     import RouterRTL
from network.routing.RoutingDORY  import RoutingDORY
from ocn_pclib.Packet             import Packet
from ocn_pclib.Position           import *

class NetworkRTL( RTLComponent ):
#  def construct( s, RouterType, RoutingStrategyType, TopologyType ):
  def construct( s ):

    s.num_outports = 5
    s.pos = MeshPosition( 2, 1, 1)
    s.RouteUnitType = RouteUnitRTL
    s.RoutingStrategyType = RoutingDORY
    s.PositionType = MeshPosition

    # Interface
    s.recv =  InEnRdyIfc( Packet )
#    s.send = OutEnRdyIfc( Packet ) 
    s.send = [ OutEnRdyIfc (Packet) for _ in range ( s.num_outports ) ]

    s.pos  = InVPort( s.PositionType )
    s.output = OutVPort( Bits3 )
#    s.output = Wire( Bits3 )

    # Components
    s.router = RouterRTL( s.RoutingStrategyType, s.RouteUnitType, s.PositionType )

    # Connections
    s.connect( s.recv.msg,   s.router.recv.msg )
    s.connect( s.pos,        s.router.pos      )
    s.connect( s.output, s.router.output   )

    for i in range( s.num_outports ):
      s.connect( s.router.send[i].rdy, s.send[i].rdy )
      s.connect( s.router.send[i].msg, s.send[i].msg )

  def line_trace( s ):
    return "pos:({},{}); src:({},{}); dst:({},{}); out_dir:({})".format(
s.pos.pos_x, s.pos.pos_y, s.recv.msg.src_x, s.recv.msg.src_y, s.recv.msg.dst_x,
s.recv.msg.dst_y, s.output )
    
