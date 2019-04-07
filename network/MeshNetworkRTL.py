#=========================================================================
# MeshNetworkRTL.py
#=========================================================================
# Mesh network implementation.
#
# Author : Cheng Tan
#   Date : Mar 10, 2019

from pymtl                       import *
from pclib.ifcs.SendRecvIfc      import *
from router.router_utils         import *
from router.MeshRouterRTL        import MeshRouterRTL
from router.InputUnitRTL         import InputUnitRTL
from router.DORYMeshRouteUnitRTL import DORYMeshRouteUnitRTL
from router.SwitchUnitRTL        import SwitchUnitRTL
from router.OutputUnitRTL        import OutputUnitRTL
from channel.ChannelRTL          import ChannelRTL

class MeshNetworkRTL( Component ):
  def construct( s, PacketType, PositionType, mesh_wid=4, mesh_ht=4,
                 channel_latency=0, routing_dimension='y' ):

    s.num_routers     = mesh_wid * mesh_ht
    s.channel_latency = 0
    mesh_ht           = mesh_ht
    mesh_wid          = mesh_wid

    RouteUnitType = DORYMeshRouteUnitRTL if routing_dimension=='y' else \
                    DORXMeshRouteUnitRTL

    # Interface
    s.recv       = [ RecvIfcRTL(PacketType) for _ in range(s.num_routers)]
    s.send       = [ SendIfcRTL(PacketType) for _ in range(s.num_routers)]

    # Components
    s.routers    = [ MeshRouterRTL( PacketType, PositionType, RouteUnitType ) 
                     for i in range(s.num_routers)]

    num_channels = 2 * (mesh_ht*(mesh_wid-1)+mesh_wid*(mesh_ht-1))

    s.channels   = [ ChannelRTL(PacketType, latency=channel_latency)
                     for _ in range( num_channels ) ]

    channel_index  = 0

    # Connect s.routers together in Mesh
    for i in range( s.num_routers ):
      if i / mesh_wid > 0:
        s.connect( s.routers[i].send[NORTH], s.channels[channel_index].recv )
        s.connect( s.channels[channel_index].send, s.routers[i-mesh_wid].recv[SOUTH] )
        channel_index += 1

      if i / mesh_wid < mesh_ht - 1:
        s.connect( s.routers[i].send[SOUTH], s.channels[channel_index].recv )
        s.connect( s.channels[channel_index].send, s.routers[i+mesh_wid].recv[NORTH] )
        channel_index += 1

      if i % mesh_wid > 0:
        s.connect( s.routers[i].send[WEST], s.channels[channel_index].recv )
        s.connect( s.channels[channel_index].send, s.routers[i-1].recv[EAST] )
        channel_index += 1

      if i % mesh_wid < mesh_wid - 1:
        s.connect( s.routers[i].send[EAST], s.channels[channel_index].recv )
        s.connect( s.channels[channel_index].send, s.routers[i+1].recv[WEST] )
        channel_index += 1

      # Connect the self port (with Network Interface)
      s.connect(s.recv[i], s.routers[i].recv[SELF])
      s.connect(s.send[i], s.routers[i].send[SELF])

      # Connect the unused ports
      if i / mesh_wid == 0:
        s.connect( s.routers[i].send[NORTH].rdy,         0 )
        s.connect( s.routers[i].recv[NORTH].en,          0 )
        s.connect( s.routers[i].recv[NORTH].msg.payload, 0 )

      if i / mesh_wid == mesh_ht - 1:
        s.connect( s.routers[i].send[SOUTH].rdy,         0 )
        s.connect( s.routers[i].recv[SOUTH].en,          0 )
        s.connect( s.routers[i].recv[SOUTH].msg.payload, 0 )

      if i % mesh_wid == 0:
        s.connect( s.routers[i].send[WEST].rdy,          0 )
        s.connect( s.routers[i].recv[WEST].en,           0 )
        s.connect( s.routers[i].recv[WEST].msg.payload,  0 )

      if i % mesh_wid == mesh_wid - 1:
        s.connect( s.routers[i].send[EAST].rdy,          0 )
        s.connect( s.routers[i].recv[EAST].en,           0 )
        s.connect( s.routers[i].recv[EAST].msg.payload,  0 )

    # FIXME: unable to connect a struct to a port.
    @s.update
    def up_pos():
      for y in range( mesh_ht ):
        for x in range( mesh_wid ):
          idx = y * mesh_wid + x
          s.routers[idx].pos = PositionType( x, y )

  def line_trace( s ):
    trace = [ "" for _ in range( s.num_routers ) ]
    for i in range( s.num_routers ):
      trace[i] = "{}".format( s.routers[i].recv )
    return "|".join( trace )
