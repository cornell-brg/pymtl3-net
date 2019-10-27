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

  def construct( s, PacketType, PositionType,
                 mesh_width=4, mesh_height=4, chl_lat=0, vc=2, credit_line=2 ):

    # Constants

    s.mesh_width    = mesh_width
    s.mesh_height   = mesh_height
    s.num_routers   = mesh_width * mesh_height
    num_channels    = mesh_height * mesh_width * 4
    s.num_terminals = s.num_routers
    XType           = mk_bits( clog2(mesh_width) )
    YType           = mk_bits( clog2(mesh_height ) )

    # Interface

    s.recv = [ RecvIfcRTL(PacketType) for _ in range(s.num_terminals)]
    s.send = [ SendIfcRTL(PacketType) for _ in range(s.num_terminals)]

    # Components

    s.routers = [ TorusRouterRTL( PacketType, PositionType,
                                  ncols=mesh_width, nrows=mesh_height,
                                  vc=vc, credit_line=credit_line )
                     for i in range( s.num_routers ) ]

    s.recv_adapters = [ RecvRTL2CreditSendRTL( PacketType, vc=vc,
        credit_line=credit_line ) for _ in range( s.num_routers ) ]
    s.send_adapters = [ CreditRecvRTL2SendRTL( PacketType, vc=vc,
        credit_line=credit_line ) for _ in range( s.num_routers ) ]

    # Connect s.routers together in Torus

    chl_id  = 0
    for i in range (s.num_routers):
      s_idx = (i-mesh_height+s.num_routers) % s.num_routers
      s.routers[i].send[SOUTH] //= s.routers[s_idx].recv[NORTH]
      s.routers[i].send[NORTH] //=\
        s.routers[(i+mesh_width+s.num_routers)%s.num_routers].recv[SOUTH]
      s.routers[i].send[WEST]  //=\
        s.routers[i-(i%mesh_width-(i-1)%mesh_width)].recv[EAST]
      s.routers[i].send[EAST]  //=\
        s.routers[i+(i+1)%mesh_width-i%mesh_width].recv[WEST]

      # Connect the self port (with Network Interface)
      s.recv[i]               //= s.recv_adapters[i].recv
      s.recv_adapters[i].send //= s.routers[i].recv[SELF]

      s.routers[i].send[SELF] //= s.send_adapters[i].recv
      s.send_adapters[i].send //= s.send[i]

#    @s.update
#    def up_pos():
    for y in range( mesh_height ):
      for x in range( mesh_width ):
#          idx = y * mesh_width + x
#          s.routers[idx].pos = PositionType( x, y )
        s.routers[y*mesh_width+x].pos.pos_x //= XType(x)
        s.routers[y*mesh_width+x].pos.pos_y //= YType(y)

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
      r.dim.x = BOUNDARY + i % s.mesh_width * ( r.dim.w + s.channels[0].dim.w )
      r.dim.y = BOUNDARY + i / s.mesh_width * ( r.dim.h + s.channels[0].dim.w )

    s.dim.w = 2 * BOUNDARY + s.mesh_width * ( r.dim.w + s.channels[0].dim.w )
    s.dim.h = 2 * BOUNDARY + s.mesh_height  * ( r.dim.h + s.channels[0].dim.w )

