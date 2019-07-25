#=========================================================================
# TorusNetworkCL.py
#=========================================================================
# Cycle level Torus network implementation.
#
# Author : Yanghui Ou
#   Date : Mar 21, 2019

from pymtl3 import *
from directions             import *
from TorusRouterCL          import TorusRouterCL
from channel.ChannelCL      import ChannelCL

class TorusNetworkCL( Component ):
  def construct( s, PacketType, PositionType, mesh_wid=4, mesh_ht=4, chl_lat=0 ):

    # Constants

    s.mesh_wid      = mesh_wid
    s.mesh_ht       = mesh_ht
    s.num_routers   = mesh_wid * mesh_ht
    num_channels    = mesh_ht * mesh_wid * 4
    s.num_terminals = s.num_routers

    # Interface

    s.recv       = [ NonBlockingCallee() for _ in range(s.num_terminals) ]
    s.send       = [ NonBlockingCaller() for _ in range(s.num_terminals) ]

    # Components

    s.routers    = [ TorusRouterCL( PacketType, PositionType )
                     for i in range( s.num_routers ) ]

    s.channels   = [ ChannelCL( PacketType, latency = chl_lat)
                     for _ in range( num_channels ) ]

    # Connect s.routers together in Torus

    chl_id  = 0
    for i in range (s.num_routers):
      # Connect s.routers together in Torus
      s.routers[i].send[SOUTH] //= s.channels[chl_id].recv
      s.channels[chl_id].send  //= s.routers[(i-mesh_ht+\
          s.num_routers)%s.num_routers].recv[NORTH]
      chl_id += 1

      s.routers[i].send[NORTH] //= s.channels[chl_id].recv
      s.channels[chl_id].send  //= s.routers[\
          (i+mesh_ht+s.num_routers)%s.num_routers].recv[SOUTH]
      chl_id += 1

      s.routers[i].send[WEST] //= s.channels[chl_id].recv
      s.channels[chl_id].send //= s.routers[\
          i-(i%mesh_wid-(i-1)%mesh_wid)].recv[EAST])
      chl_id += 1

      s.routers[i].send[EAST] //= s.channels[chl_id].recv
      s.channels[chl_id].send //= s.routers[\
          i+(i+1)%mesh_wid-i%mesh_wid].recv[WEST])
      chl_id += 1

      # Connect the self port (with Network Interface)
      s.recv[i] //= s.routers[i].recv[SELF]
      s.send[i] //= s.routers[i].send[SELF]

    @s.update
    def up_pos():
      for y in range( mesh_ht ):
        for x in range( mesh_wid ):
          idx = y * mesh_wid + x
          s.routers[idx].pos = PositionType( x, y )

  def line_trace( s ):
    trace = [ "" for _ in range( s.num_terminals ) ]
    for i in range( s.num_terminals ):
      trace[i] += s.routers[i].line_trace()
    return "|".join( trace )

  def elaborate_physical( s ):
    # Initialize dimension for sub-modules.
    BOUNDARY = 10

    for i, r in enumerate( s.routers ):
      r.dim.x = BOUNDARY + i % s.mesh_wid * ( r.dim.w + s.channels[0].dim.w )
      r.dim.y = BOUNDARY + i / s.mesh_wid * ( r.dim.h + s.channels[0].dim.w )

    s.dim.w = 2 * BOUNDARY + s.mesh_wid * ( r.dim.w + s.channels[0].dim.w )
    s.dim.h = 2 * BOUNDARY + s.mesh_ht  * ( r.dim.h + s.channels[0].dim.w )
