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
from network.topology.Mesh        import Mesh
from ocn_pclib.Packet             import Packet
from ocn_pclib.Position           import *

class NetworkRTL( RTLComponent ):
#  def construct( s, RouterType, RoutingStrategyType, TopologyType ):
  def construct( s ):

    s.num_outports = 5
    s.num_routers  = 2
    s.pos = MeshPosition( 2, 1, 1)
    s.RouteUnitType = RouteUnitRTL
    s.RoutingStrategyType = RoutingDORY
    s.PositionType = MeshPosition

    s.TopologyType = Mesh
    s.topology = s.TopologyType()

    # Interface
    s.recv = InEnRdyIfc( Packet )
#    s.send = OutEnRdyIfc( Packet ) 
    s.send = [ OutEnRdyIfc( Packet ) for _ in range ( s.num_outports * s.num_routers ) ]

    s.pos  = InVPort( s.PositionType )
    s.outputs = [ OutVPort( Bits3 ) for _ in range( s.num_routers ) ]
#    s.output = Wire( Bits3 )

    # Components
    s.routers = [ RouterRTL( _, s.RoutingStrategyType, s.RouteUnitType, s.PositionType ) 
                  for _ in range( s.num_routers ) ]

    # Connections
    for i in range( s.num_routers ):
      s.connect( s.recv.msg, s.routers[i].recv.msg )
      s.connect( s.pos,         s.routers[i].pos      )
      s.connect( s.outputs[i],  s.routers[i].output   )

    for i in range( s.num_routers ):
      for j in range( s.num_outports ):
        s.connect( s.routers[i].send[j].rdy, s.send[i * s.num_outports + j].rdy )
        s.connect( s.routers[i].send[j].msg, s.send[i * s.num_outports + j].msg )
    
    s.topology.mkTopology( s.routers )

  def line_trace( s ):
    return "pos:({},{}); src:({},{}); dst:({},{}); out_dir:({})".format(
s.pos.pos_x, s.pos.pos_y, s.recv.msg.src_x, s.recv.msg.src_y, s.recv.msg.dst_x,
s.recv.msg.dst_y, s.outputs )
    
