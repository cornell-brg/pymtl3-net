#=========================================================================
# TorusNetworkRTL.py
#=========================================================================
# Torus network implementation.
#
# Author : Cheng Tan
#   Date : Mar 10, 2019

from pymtl3                   import *
from channel.ChannelRTL       import ChannelRTL
from directions               import *
from pymtl3.stdlib.ifcs       import SendIfcRTL, RecvIfcRTL
from TorusRouterRTL           import TorusRouterRTL
from ocn_pclib.ifcs.CreditIfc import RecvRTL2CreditSendRTL, CreditRecvRTL2SendRTL

class TorusNetworkRTL( Component ):

  def construct( s,
                 PacketType,
                 PositionType,
                 mesh_wid=4,
                 mesh_ht=4,
                 chl_lat=0,
                 nvcs=2,
                 credit_line=2,
               ):

    # Constants

    s.mesh_wid      = mesh_wid
    s.mesh_ht       = mesh_ht
    s.num_routers   = mesh_wid * mesh_ht
    num_channels    = mesh_ht * mesh_wid * 4
    s.num_terminals = s.num_routers

    # Interface

    s.recv       = [ RecvIfcRTL(PacketType) for _ in range(s.num_terminals)]
    s.send       = [ SendIfcRTL(PacketType) for _ in range(s.num_terminals)]

    # Components

    s.routers    = [ TorusRouterRTL( PacketType, PositionType, ncols=mesh_wid, nrows=mesh_ht, nvcs=nvcs, credit_line=credit_line )
                     for i in range( s.num_routers ) ]

    s.recv_adapters = [ RecvRTL2CreditSendRTL( PacketType, nvcs=nvcs,
        credit_line=credit_line ) for _ in range( s.num_routers ) ]
    s.send_adapters = [ CreditRecvRTL2SendRTL( PacketType, nvcs=nvcs,
        credit_line=credit_line ) for _ in range( s.num_routers ) ]

#    s.channels   = [ ChannelRTL( PacketType, latency = chl_lat)
#                     for _ in range( num_channels ) ]

    # Connect s.routers together in Torus

    chl_id  = 0
    for i in range (s.num_routers):
      # Connect s.routers together in Torus
      s.connect( s.routers[i].send[SOUTH],
                 s.routers[(i-mesh_wid+s.num_routers)%s.num_routers].recv[NORTH])
      s.connect( s.routers[i].send[NORTH],
                 s.routers[(i+mesh_wid+s.num_routers)%s.num_routers].recv[SOUTH])
      s.connect( s.routers[i].send[WEST],
                 s.routers[i-(i%mesh_wid-(i-1)%mesh_wid)].recv[EAST])
      s.connect( s.routers[i].send[EAST],
                 s.routers[i+(i+1)%mesh_wid-i%mesh_wid].recv[WEST])

#      s.connect(s.routers[i].send[SOUTH], s.channels[chl_id].recv)
#      s.connect(s.channels[chl_id].send, s.routers[(i-mesh_ht+
#          s.num_routers)%s.num_routers].recv[NORTH])
#      chl_id += 1
#
#      s.connect(s.routers[i].send[NORTH], s.channels[chl_id].recv)
#      s.connect(s.channels[chl_id].send, s.routers[
#          (i+mesh_ht+s.num_routers)%s.num_routers].recv[SOUTH])
#      chl_id += 1
#
#      s.connect(s.routers[i].send[WEST],  s.channels[chl_id].recv)
#      s.connect(s.channels[chl_id].send, s.routers[
#          i-(i%mesh_wid-(i-1)%mesh_wid)].recv[EAST])
#      chl_id += 1
#
#      s.connect(s.routers[i].send[EAST],  s.channels[chl_id].recv)
#      s.connect(s.channels[chl_id].send, s.routers[
#          i+(i+1)%mesh_wid-i%mesh_wid].recv[WEST])
#      chl_id += 1

      # Connect the self port (with Network Interface)
      s.connect( s.recv[i],               s.recv_adapters[i].recv )
      s.connect( s.recv_adapters[i].send, s.routers[i].recv[SELF] )

      s.connect( s.routers[i].send[SELF], s.send_adapters[i].recv )
      s.connect( s.send_adapters[i].send, s.send[i]               )

#      s.connect(s.recv[i], s.routers[i].recv[SELF])
#      s.connect(s.send[i], s.routers[i].send[SELF])

    @s.update
    def up_pos():
      for y in range( mesh_ht ):
        for x in range( mesh_wid ):
          idx = y * mesh_wid + x
          s.routers[idx].pos = PositionType( x, y )

  def line_trace( s ):
    in_trace  = [ str( s.recv[i] ) for i in range( s.num_terminals ) ]
    out_trace = [ str( s.send[i] ) for i in range( s.num_terminals ) ]

    # return "{}_()_{}".format( "|".join( in_trace ), "|".join( out_trace ) )
    return "{}".format( "|".join( out_trace ) )

  def elaborate_physical( s ):
    # Initialize dimension for sub-modules.
    BOUNDARY = 10

    for i, r in enumerate( s.routers ):
      r.dim.x = BOUNDARY + i % s.mesh_wid * ( r.dim.w + s.channels[0].dim.w )
      r.dim.y = BOUNDARY + i / s.mesh_wid * ( r.dim.h + s.channels[0].dim.w )

    s.dim.w = 2 * BOUNDARY + s.mesh_wid * ( r.dim.w + s.channels[0].dim.w )
    s.dim.h = 2 * BOUNDARY + s.mesh_ht  * ( r.dim.h + s.channels[0].dim.w )

