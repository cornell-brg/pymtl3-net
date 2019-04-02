#=========================================================================
# TorusNetworkRTL.py
#=========================================================================
# Torus network implementation.
#
# Author : Cheng Tan
#   Date : Mar 10, 2019

from pymtl                        import *
from pclib.ifcs.SendRecvIfc       import *
from router.MeshRouterRTL         import MeshRouterRTL
from router.InputUnitRTL          import InputUnitRTL
from router.DORXMeshRouteUnitRTL  import DORXMeshRouteUnitRTL
from router.DORYMeshRouteUnitRTL  import DORYMeshRouteUnitRTL
from router.DORYTorusRouteUnitRTL import DORYTorusRouteUnitRTL
from router.SwitchUnitRTL         import SwitchUnitRTL
from router.OutputUnitRTL         import OutputUnitRTL
from channel.ChannelRTL           import ChannelRTL

class TorusNetworkRTL( ComponentLevel6 ):
  def construct( s, PacketType, PositionType, mesh_wid=4, mesh_ht=4,
                 channel_latency=0 ):
    # Constants

    NORTH = 0
    SOUTH = 1
    WEST  = 2
    EAST  = 3
    SELF  = 4

    s.num_routers     = mesh_wid * mesh_ht
    s.channel_latency = 0
    mesh_ht            = mesh_ht
    mesh_wid            = mesh_wid

    RouteUnitType   = DORYTorusRouteUnitRTL

    # Interface
    s.recv = [ RecvIfcRTL(PacketType) for _ in range( s.num_routers ) ]
    s.send = [ SendIfcRTL(PacketType) for _ in range( s.num_routers ) ]

    # Components
    s.routers = [ MeshRouterRTL(PacketType, PositionType, RouteUnitType ) 
                  for i in range(s.num_routers)]

    num_channels = 4 * mesh_ht * mesh_wid

    s.channels   = [ ChannelRTL( PacketType, latency=s.channel_latency)
                     for _ in range(num_channels) ]

    channel_index  = 0

    for i in range (s.num_routers):
      # Connect s.routers together in Torus
      s.connect(s.routers[i].send[NORTH], s.channels[channel_index].recv)
      s.connect(s.channels[channel_index].send, s.routers[(i-mesh_ht+
          s.num_routers)%s.num_routers].recv[SOUTH])
      channel_index += 1
 
      s.connect(s.routers[i].send[SOUTH], s.channels[channel_index].recv)
      s.connect(s.channels[channel_index].send, s.routers[
          (i+mesh_ht+s.num_routers)%s.num_routers].recv[NORTH])
      channel_index += 1
 
      s.connect(s.routers[i].send[WEST],  s.channels[channel_index].recv)
      s.connect(s.channels[channel_index].send, s.routers[
          i-(i%mesh_wid-(i-1)%mesh_wid)].recv[EAST])
      channel_index += 1
 
      s.connect(s.routers[i].send[EAST],  s.channels[channel_index].recv)
      s.connect(s.channels[channel_index].send, s.routers[
          i+(i+1)%mesh_wid-i%mesh_wid].recv[WEST])
      channel_index += 1

      # Connect the self port (with Network Interface)
      s.connect(s.recv[i], s.routers[i].recv[SELF])
      s.connect(s.send[i], s.routers[i].send[SELF])

    @s.update
    def up_pos():
      for y in range( mesh_ht ):
        for x in range( mesh_wid ):
          idx = y * mesh_wid + x
          s.routers[idx].pos = PositionType( x, y )

  def line_trace( s ):
    trace = ''
    for r in range(s.num_routers):
      trace += '\n({},{})|'.format(s.routers[r].pos.pos_x, s.routers[r].pos.pos_y)
      for i in range(s.routers[r].num_inports):
        if isinstance(s.routers[r].recv[i].msg, int):
          trace += '|{}'.format(s.routers[r].recv[i].msg)
        else:
          trace += '|{}:{}->({},{})'.format( i, 
                s.routers[r].recv[i].msg.payload, 
                s.routers[r].recv[i].msg.dst_x,
                s.routers[r].recv[i].msg.dst_y)
      trace += '\n out: '
      for i in range(s.routers[r].num_outports):
        if isinstance(s.routers[r].recv[i].msg, int):
          trace += '|{}'.format(s.routers[r].recv[i].msg)
        else:
          trace += '|{}:{}->({},{})'.format( i, 
                s.routers[r].send[i].msg.payload, 
                s.routers[r].send[i].msg.dst_x,
                s.routers[r].send[i].msg.dst_y)
    return trace
    
