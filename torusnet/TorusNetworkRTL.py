#=========================================================================
# TorusNetworkRTL.py
#=========================================================================
# Torus network implementation.
#
# Author : Cheng Tan
#   Date : Mar 10, 2019

from channel.ChannelRTL import ChannelRTL
from ocn_pclib.ifcs.CreditIfc import (CreditRecvRTL2SendRTL,
                                      RecvRTL2CreditSendRTL)
from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL

from .directions import *
from .TorusRouterRTL import TorusRouterRTL


class TorusNetworkRTL( Component ):

  def construct( s, PacketType, PositionType,
                 ncols=4, nrows=4, chl_lat=0, vc=2, credit_line=2 ):

    # Constants

    s.ncols = ncols
    s.nrows = nrows
    s.num_routers   = ncols * nrows
    s.num_terminals = s.num_routers
    XType           = mk_bits( clog2(ncols) )
    YType           = mk_bits( clog2(nrows ) )

    # Interface

    s.recv = [ RecvIfcRTL(PacketType) for _ in range(s.num_terminals)]
    s.send = [ SendIfcRTL(PacketType) for _ in range(s.num_terminals)]

    # Components

    s.routers = [ TorusRouterRTL( PacketType, PositionType,
                                  ncols=ncols, nrows=nrows,
                                  vc=vc, credit_line=credit_line )
                     for i in range( s.num_routers ) ]

    s.recv_adapters = [ RecvRTL2CreditSendRTL( PacketType, vc=vc,
        credit_line=credit_line ) for _ in range( s.num_routers ) ]
    s.send_adapters = [ CreditRecvRTL2SendRTL( PacketType, vc=vc,
        credit_line=credit_line ) for _ in range( s.num_routers ) ]

    # Connect s.routers together in Torus

    chl_id  = 0
    for i in range (s.num_routers):
      s_idx = (i-nrows+s.num_routers) % s.num_routers
      s.routers[i].send[SOUTH] //= s.routers[s_idx].recv[NORTH]
      s.routers[i].send[NORTH] //=\
        s.routers[(i+ncols+s.num_routers)%s.num_routers].recv[SOUTH]
      s.routers[i].send[WEST]  //=\
        s.routers[i-(i%ncols-(i-1)%ncols)].recv[EAST]
      s.routers[i].send[EAST]  //=\
        s.routers[i+(i+1)%ncols-i%ncols].recv[WEST]

      # Connect the self port (with Network Interface)
      s.recv[i]               //= s.recv_adapters[i].recv
      s.recv_adapters[i].send //= s.routers[i].recv[SELF]

      s.routers[i].send[SELF] //= s.send_adapters[i].recv
      s.send_adapters[i].send //= s.send[i]

#    @s.update
#    def up_pos():
    for y in range( nrows ):
      for x in range( ncols ):
#          idx = y * ncols + x
#          s.routers[idx].pos = PositionType( x, y )
        s.routers[y*ncols+x].pos.pos_x //= XType(x)
        s.routers[y*ncols+x].pos.pos_y //= YType(y)

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
      r.dim.x = BOUNDARY + i % s.ncols * ( r.dim.w + s.channels[0].dim.w )
      r.dim.y = BOUNDARY + i / s.ncols * ( r.dim.h + s.channels[0].dim.w )

    s.dim.w = 2 * BOUNDARY + s.ncols * ( r.dim.w + s.channels[0].dim.w )
    s.dim.h = 2 * BOUNDARY + s.nrows  * ( r.dim.h + s.channels[0].dim.w )
