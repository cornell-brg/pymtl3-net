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
  def construct( s, PacketType, PositionType,
                    mesh_width=4, mesh_height=4, chl_lat=0 ):

    # Constants

    s.mesh_width    = mesh_width
    s.mesh_height   = mesh_height
    s.num_routers   = mesh_width * mesh_height
    num_channels    = mesh_height * mesh_width * 4
    s.num_terminals = s.num_routers

    # Interface

    s.recv = [ NonBlockingCallee() for _ in range(s.num_terminals) ]
    s.send = [ NonBlockingCaller() for _ in range(s.num_terminals) ]

    # Components

    s.routers  = [ TorusRouterCL( PacketType, PositionType )
                    for i in range( s.num_routers ) ]

    s.channels = [ ChannelCL( PacketType, latency = chl_lat)
                    for _ in range( num_channels ) ]

    # Connect routers in Torus

    chl_id  = 0
    for i in range (s.num_routers):

      s_idx = (i-mesh_height+s.num_routers) % s.num_routers
      s.routers[i].send[SOUTH] //= s.channels[chl_id].recv
      s.channels[chl_id].send  //= s.routers[s_idx].recv[NORTH]
      chl_id += 1

      n_idx = (i+mesh_height+s.num_routers) % s.num_routers
      s.routers[i].send[NORTH] //= s.channels[chl_id].recv
      s.channels[chl_id].send  //= s.routers[n_idx].recv[SOUTH]
      chl_id += 1

      w_idx = i - ( i % mesh_width - (i-1) % mesh_width )
      s.routers[i].send[WEST] //= s.channels[chl_id].recv
      s.channels[chl_id].send //= s.routers[w_idx].recv[EAST]
      chl_id += 1

      e_idx = i + (i+1) % mesh_width - i % mesh_width
      s.routers[i].send[EAST] //= s.channels[chl_id].recv
      s.channels[chl_id].send //= s.routers[e_idx].recv[WEST]
      chl_id += 1

      # Connect the self port (with Network Interface)

      s.recv[i] //= s.routers[i].recv[SELF]
      s.send[i] //= s.routers[i].send[SELF]

    @s.update
    def up_pos():
      for y in range( mesh_height ):
        for x in range( mesh_width ):
          idx = y * mesh_width + x
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
      r.dim.x = BOUNDARY + i % s.mesh_width * ( r.dim.w + s.channels[0].dim.w )
      r.dim.y = BOUNDARY + i / s.mesh_width * ( r.dim.h + s.channels[0].dim.w )

    s.dim.w = 2 * BOUNDARY + s.mesh_width * ( r.dim.w + s.channels[0].dim.w )
    s.dim.h = 2 * BOUNDARY + s.mesh_height  * ( r.dim.h + s.channels[0].dim.w )
