#=========================================================================
# TorusNetworkRTL.py
#=========================================================================
# Torus network implementation.
#
# Author : Cheng Tan
#   Date : Mar 10, 2019

from pymtl3                   import *
from channel.ChannelRTL       import ChannelRTL
from .directions              import *
from pymtl3.stdlib.ifcs       import SendIfcRTL, RecvIfcRTL
from .TorusRouterRTL          import TorusRouterRTL
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
    XType           = mk_bits( clog2(mesh_wid) )
    YType           = mk_bits( clog2(mesh_ht ) )

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

    # Connect s.routers together in Torus

    chl_id  = 0
    for i in range (s.num_routers):
      s_idx = (i-mesh_ht+s.num_routers) % s.num_routers
      s.routers[i].send[SOUTH] //= s.routers[s_idx].recv[NORTH]
      s.routers[i].send[NORTH] //=\
        s.routers[(i+mesh_wid+s.num_routers)%s.num_routers].recv[SOUTH]
      s.routers[i].send[WEST]  //=\
        s.routers[i-(i%mesh_wid-(i-1)%mesh_wid)].recv[EAST]
      s.routers[i].send[EAST]  //=\
        s.routers[i+(i+1)%mesh_wid-i%mesh_wid].recv[WEST]

      # Connect the self port (with Network Interface)
      s.recv[i]               //= s.recv_adapters[i].recv
      s.recv_adapters[i].send //= s.routers[i].recv[SELF]

      s.routers[i].send[SELF] //= s.send_adapters[i].recv
      s.send_adapters[i].send //= s.send[i]

#    @s.update
#    def up_pos():
    for y in range( mesh_ht ):
      for x in range( mesh_wid ):
#          idx = y * mesh_wid + x
#          s.routers[idx].pos = PositionType( x, y )
        s.routers[y*mesh_wid+x].pos.pos_x //= XType(x)
        s.routers[y*mesh_wid+x].pos.pos_y //= YType(y)

  def line_trace( s ):
      send_lst = []
      recv_lst = []
      for r in s.routers:
        has_recv = any([ r.recv[i].en for i in range(5) ])
        has_send = any([ r.send[i].en for i in range(5) ])
        if has_send:
          send_lst.append( f'{r.pos}' )
        if has_recv:
          recv_lst.append( f'{r.pos}')
      send_str = ','.join( send_lst )
      recv_str = ','.join( recv_lst )
      return f' {send_str:3} -> {recv_str:3}'


  def elaborate_physical( s ):
    # Initialize dimension for sub-modules.
    BOUNDARY = 10

    for i, r in enumerate( s.routers ):
      r.dim.x = BOUNDARY + i % s.mesh_wid * ( r.dim.w + s.channels[0].dim.w )
      r.dim.y = BOUNDARY + i / s.mesh_wid * ( r.dim.h + s.channels[0].dim.w )

    s.dim.w = 2 * BOUNDARY + s.mesh_wid * ( r.dim.w + s.channels[0].dim.w )
    s.dim.h = 2 * BOUNDARY + s.mesh_ht  * ( r.dim.h + s.channels[0].dim.w )

