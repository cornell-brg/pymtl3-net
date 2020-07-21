"""
=========================================================================
MeshNetworkRTL.py
=========================================================================
Mesh network implementation.

Author : Yanghui Ou, Cheng Tan
  Date : Mar 10, 2019
"""
from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL

from channel.ChannelRTL import ChannelRTL

from .directions import *
from .MeshRouterRTL import MeshRouterRTL


class MeshNetworkRTL( Component ):
  def construct( s, PacketType, PositionType,
                 ncols=4, nrows=4, chl_lat=0 ):

    # Local parameters

    s.num_routers   = ncols * nrows
    s.num_terminals = s.num_routers
    num_channels    = (nrows*(ncols-1)+ncols*(nrows-1)) * 2
    XType           = mk_bits( clog2(ncols) )
    YType           = mk_bits( clog2(nrows ) )

    # Interface

    s.recv = [ RecvIfcRTL( PacketType ) for _ in range( s.num_terminals )]
    s.send = [ SendIfcRTL( PacketType ) for _ in range( s.num_terminals )]

    # Components

    s.routers  = [ MeshRouterRTL( PacketType, PositionType )
                   for _ in range( s.num_routers ) ]

    s.channels = [ ChannelRTL( PacketType, latency = chl_lat )
                   for _ in range( num_channels ) ]

    # Wire the position ports of router

    for y in range( nrows ):
      for x in range( ncols ):
        s.routers[y*ncols+x].pos.pos_x //= x
        s.routers[y*ncols+x].pos.pos_y //= y

    # Connect routers together in Mesh
    # NOTE: for now we put all channels in a single list. In the future we
    # may want to divide channels into different groups so that it is
    # easier to configure.

    chl_id  = 0
    for i in range( s.num_routers ):
      if i // ncols > 0:
        s.routers[i].send[SOUTH] //= s.channels[chl_id].recv
        s.channels[chl_id].send  //= s.routers[i-ncols].recv[NORTH]
        chl_id += 1

      if i // ncols < nrows - 1:
        s.routers[i].send[NORTH] //= s.channels[chl_id].recv
        s.channels[chl_id].send  //= s.routers[i+ncols].recv[SOUTH]
        chl_id += 1

      if i % ncols > 0:
        s.routers[i].send[WEST] //= s.channels[chl_id].recv
        s.channels[chl_id].send //= s.routers[i-1].recv[EAST]
        chl_id += 1

      if i % ncols < ncols - 1:
        s.routers[i].send[EAST] //= s.channels[chl_id].recv
        s.channels[chl_id].send //= s.routers[i+1].recv[WEST]
        chl_id += 1

      # Connect the self port (with Network Interface)

      s.recv[i] //= s.routers[i].recv[SELF]
      s.send[i] //= s.routers[i].send[SELF]

      # Connect the unused ports
      # FIXME: for now we hackily ground the payload field so that pymtl
      # won't complain about net need driver.

      if i // ncols == 0:
        s.routers[i].send[SOUTH].rdy         //= 0
        s.routers[i].recv[SOUTH].en          //= 0
        s.routers[i].recv[SOUTH].msg.payload //= 0

      if i // ncols == nrows - 1:
        s.routers[i].send[NORTH].rdy         //= 0
        s.routers[i].recv[NORTH].en          //= 0
        s.routers[i].recv[NORTH].msg.payload //= 0

      if i % ncols == 0:
        s.routers[i].send[WEST].rdy          //= 0
        s.routers[i].recv[WEST].en           //= 0
        s.routers[i].recv[WEST].msg.payload  //= 0

      if i % ncols == ncols - 1:
        s.routers[i].send[EAST].rdy          //= 0
        s.routers[i].recv[EAST].en           //= 0
        s.routers[i].recv[EAST].msg.payload  //= 0

  def line_trace( s ):
    trace    = []
    send_lst = []
    recv_lst = []
    for r in s.routers:
      has_recv = any([ r.recv[i].en for i in range(5) ])
      has_send = any([ r.send[i].en for i in range(5) ])
      if has_send:
        send_lst.append( f'{r.pos}' )
      if has_recv:
        recv_lst.append( f'{r.pos}')
      if has_recv or has_send:
        trace.append( f'  {r.line_trace()}')
    send_str = ','.join( send_lst )
    recv_str = ','.join( recv_lst )
    return f' {send_str:3} -> {recv_str:3}' # + '\n'.join( trace )
