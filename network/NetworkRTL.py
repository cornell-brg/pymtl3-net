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
    s.num_inports = 5
    s.num_routers  = 2
    s.pos = MeshPosition( 2, 1, 1)
    s.RouteUnitType = RouteUnitRTL
    s.RoutingStrategyType = RoutingDORY
    s.PositionType = MeshPosition

    s.TopologyType = Mesh
    s.topology = s.TopologyType()

    # Interface
    s.recv = [  InEnRdyIfc( Packet ) for _ in range( s.num_routers *  s.num_inports ) ]
    s.send = [ OutEnRdyIfc( Packet ) for _ in range( s.num_routers * s.num_outports ) ]

    s.outputs = [ Wire( Bits3 )  for _ in range( s.num_routers *  s.num_inports ) ]

    s.pos  = InVPort( s.PositionType )

    # Components
    s.routers = [ RouterRTL( i, s.RoutingStrategyType, s.PositionType ) 
                for i in range( s.num_routers ) ]

    # Connections
    for i in range( s.num_routers ):
      for j in range( s.num_inports):
        s.connect( s.recv[i * s.num_inports + j], s.routers[i].recv[j] )
        s.connect( s.outputs[i*s.num_inports+j],  s.routers[i].outs[j]   )
      s.connect( s.pos, s.routers[i].pos )

    for i in range( s.num_routers ):
      for j in range( s.num_outports ):
        s.connect( s.routers[i].send[j], s.send[i * s.num_outports + j] )
    
    s.topology.mkTopology( s.routers )

  # TODO: Implement line trace.
  def line_trace( s ):
    return "pos:({},{}); src:({},{}); dst:({},{}); out_dir:({})".format(
s.pos.pos_x, s.pos.pos_y, s.recv[0].msg.src_x, s.recv[0].msg.src_y, s.recv[0].msg.dst_x,
s.recv[0].msg.dst_y, s.outputs[0] )
    
