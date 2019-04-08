#=========================================================================
# RingNetworkRTL.py
#=========================================================================
# Ring network implementation.
#
# Author : Cheng Tan
#   Date : April 6, 2019

from pymtl                   import *
from pclib.ifcs.SendRecvIfc  import *
from router.RingRouterRTL    import RingRouterRTL
from router.InputUnitRTL     import InputUnitRTL
from router.RingRouteUnitRTL import RingRouteUnitRTL
from router.SwitchUnitRTL    import SwitchUnitRTL
from router.OutputUnitRTL    import OutputUnitRTL
from channel.ChannelRTL      import ChannelRTL

class RingNetworkRTL( Component ):
  def construct( s, PacketType, PositionType, num_routers=4, channel_latency=0 ):
    # Constants

    LEFT  = 0
    RIGHT = 1
    SELF  = 2

    s.num_routers     = num_routers
    s.channel_latency = 0

    RouteUnitType = RingRouteUnitRTL

    # Interface
    s.recv       = [ RecvIfcRTL(PacketType) for _ in range(s.num_routers)]
    s.send       = [ SendIfcRTL(PacketType) for _ in range(s.num_routers)]

    # Components
    s.routers    = [ RingRouterRTL( PacketType, PositionType, RouteUnitType ) 
                     for i in range(s.num_routers)]

    num_channels = num_routers * 2

    s.channels   = [ ChannelRTL(PacketType, latency=channel_latency)
                     for _ in range( num_channels ) ]

    chl_id = 0

    # Connect s.routers together in Mesh
    for i in range( s.num_routers ):
      s.connect( s.routers[i].send[RIGHT], s.channels[chl_id].recv                   )
      s.connect( s.channels[chl_id].send,  s.routers[(i+1)%s.num_routers].recv[LEFT] )
      chl_id += 1

      s.connect( s.routers[(i+1)%s.num_routers].send[LEFT], s.channels[chl_id].recv  )
      s.connect( s.channels[chl_id].send,                   s.routers[i].recv[RIGHT] )
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
    trace = [ "" for _ in range( s.num_routers ) ]
    for i in range( s.num_routers ):
      trace[i] = "{}".format( s.routers[i].recv )
    return "|".join( trace )
