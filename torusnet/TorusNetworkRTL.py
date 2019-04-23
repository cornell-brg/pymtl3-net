#=========================================================================
# TorusNetworkRTL.py
#=========================================================================
# Torus network implementation.
#
# Author : Cheng Tan
#   Date : Mar 10, 2019

from pymtl                  import *
from channel.ChannelRTL     import ChannelRTL
from Direction              import *
from pclib.ifcs.SendRecvIfc import *
from meshnet.MeshRouterRTL  import MeshRouterRTL

class TorusNetworkRTL( Component ):
  def construct( s, PacketType, PositionType, mesh_wid=4, mesh_ht=4, chl_lat=0 ):

    # Constants

    s.num_routers   = mesh_wid * mesh_ht
    num_channels    = mesh_ht * mesh_wid * 4
    s.num_terminals = s.num_routers

    # Interface

    s.recv       = [ RecvIfcRTL(PacketType) for _ in range(s.num_terminals)]
    s.send       = [ SendIfcRTL(PacketType) for _ in range(s.num_terminals)]

    # Components

    s.routers    = [ MeshRouterRTL( PacketType, PositionType )
                     for i in range( s.num_routers ) ]

    s.channels   = [ ChannelRTL( PacketType, latency = chl_lat)
                     for _ in range( num_channels ) ]

    # Connect s.routers together in Torus

    chl_id  = 0
    for i in range (s.num_routers):
      # Connect s.routers together in Torus
      s.connect(s.routers[i].send[NORTH], s.channels[chl_id].recv)
      s.connect(s.channels[chl_id].send, s.routers[(i-mesh_ht+
          s.num_routers)%s.num_routers].recv[SOUTH])
      chl_id += 1
 
      s.connect(s.routers[i].send[SOUTH], s.channels[chl_id].recv)
      s.connect(s.channels[chl_id].send, s.routers[
          (i+mesh_ht+s.num_routers)%s.num_routers].recv[NORTH])
      chl_id += 1
 
      s.connect(s.routers[i].send[WEST],  s.channels[chl_id].recv)
      s.connect(s.channels[chl_id].send, s.routers[
          i-(i%mesh_wid-(i-1)%mesh_wid)].recv[EAST])
      chl_id += 1
 
      s.connect(s.routers[i].send[EAST],  s.channels[chl_id].recv)
      s.connect(s.channels[chl_id].send, s.routers[
          i+(i+1)%mesh_wid-i%mesh_wid].recv[WEST])
      chl_id += 1

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
    trace = [ "" for _ in range( s.num_terminals ) ]
    for i in range( s.num_terminals ):
      trace[i] += s.send[i].line_trace()
    return "|".join( trace )

#  def line_trace( s ):
#    trace = ''
#    for r in range(s.num_routers):
#      trace += '\n({},{})|'.format(s.routers[r].pos.pos_x, s.routers[r].pos.pos_y)
#      for i in range(s.routers[r].num_inports):
#        if isinstance(s.routers[r].recv[i].msg, int):
#          trace += '|{}'.format(s.routers[r].recv[i].msg)
#        else:
#          trace += '|{}:{}->({},{})'.format( i, 
#                s.routers[r].recv[i].msg.payload, 
#                s.routers[r].recv[i].msg.dst_x,
#                s.routers[r].recv[i].msg.dst_y)
#      trace += '\n out: '
#      for i in range(s.routers[r].num_outports):
#        if isinstance(s.routers[r].recv[i].msg, int):
#          trace += '|{}'.format(s.routers[r].recv[i].msg)
#        else:
#          trace += '|{}:{}->({},{})'.format( i, 
#                s.routers[r].send[i].msg.payload, 
#                s.routers[r].send[i].msg.dst_x,
#                s.routers[r].send[i].msg.dst_y)
#    return trace
    
