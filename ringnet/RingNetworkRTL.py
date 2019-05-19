#=========================================================================
# RingNetworkRTL.py
#=========================================================================
# Ring network implementation.
#
# Author : Cheng Tan
#   Date : April 6, 2019

from pymtl                  import *
from pclib.ifcs.SendRecvIfc import *
from directions              import *
from RingRouterRTL          import RingRouterRTL
from channel.ChannelRTL     import ChannelRTL

class RingNetworkRTL( Component ):
  def construct( s, PacketType, PositionType, num_routers=4, chl_lat=0 ):

    # Constants

    s.num_routers = num_routers
    num_channels  = num_routers * 2
    s.num_terminals = num_routers

    # Interface

    s.recv       = [ RecvIfcRTL(PacketType) for _ in range(s.num_terminals)]
    s.send       = [ SendIfcRTL(PacketType) for _ in range(s.num_terminals)]

    # Components

    s.routers    = [ RingRouterRTL( PacketType, PositionType )
                     for i in range( s.num_routers ) ]

    s.channels   = [ ChannelRTL( PacketType, latency = chl_lat)
                     for _ in range( num_channels ) ]

    # Connect s.routers together in Mesh

    chl_id = 0
    for i in range( s.num_routers ):
      s.connect( s.routers[i].send[RIGHT], s.channels[chl_id].recv                   )
      s.connect( s.channels[chl_id].send,  s.routers[(i+1)%num_routers].recv[LEFT] )
      chl_id += 1

      s.connect( s.routers[(i+1)%num_routers].send[LEFT], s.channels[chl_id].recv  )
      s.connect( s.channels[chl_id].send,                 s.routers[i].recv[RIGHT] )
      chl_id += 1

      # Connect the self port (with Network Interface)

      s.connect(s.recv[i], s.routers[i].recv[SELF])
      s.connect(s.send[i], s.routers[i].send[SELF])

    # FIXME: unable to connect a struct to a port.
    @s.update
    def up_pos():
      for r in range( s.num_routers ):
        s.routers[r].pos = PositionType( r )

  def line_trace( s ):
    trace = [ "" for _ in range( s.num_terminals ) ]
    for i in range( s.num_terminals ):
      trace[i] += s.send[i].line_trace()
    return "|".join( trace )

  def elaborate_physical( s ):
    # Initialize dimension for sub-modules.
    BOUNDARY = 10
    MAX = len( s.routers )

    for i, r in enumerate( s.routers ):
      if i < (MAX / 2):
        r.dim.x = BOUNDARY + i * ( r.dim.w + s.channels[0].dim.w )
        r.dim.y = BOUNDARY
      else:
        r.dim.x = BOUNDARY + (MAX - i - 1) * ( r.dim.w + s.channels[0].dim.w )
        r.dim.y = BOUNDARY + r.dim.h + s.channels[0].dim.w
    s.dim.w = MAX/2 * r.dim.w + (MAX/2 - 1) * s.channels[0].dim.w
    s.dim.h = 2 * r.dim.h + s.channels[0].dim.w
