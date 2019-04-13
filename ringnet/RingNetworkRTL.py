#=========================================================================
# RingNetworkRTL.py
#=========================================================================
# Ring network implementation.
#
# Author : Cheng Tan
#   Date : April 6, 2019

from pymtl                  import *
from network.Network        import Network
from pclib.ifcs.SendRecvIfc import *
from Direction              import *
from RingRouterRTL          import RingRouterRTL
from channel.ChannelRTL     import ChannelRTL

class RingNetworkRTL( Network ):
  def construct( s, PacketType, PositionType, num_routers=4, chl_lat=0 ):

    # Constants

    s.num_routers = num_routers
    num_channels  = num_routers * 2

    super( RingNetworkRTL, s ).construct( PacketType, PositionType,
      RingRouterRTL, ChannelRTL, SendIfcRTL, RecvIfcRTL, s.num_routers,
      s.num_routers, num_channels, chl_lat )

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
