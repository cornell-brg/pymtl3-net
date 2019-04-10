#=========================================================================
# Network.py
#=========================================================================
# Network implementation.
#
# Author : Cheng Tan
#   Date : April 10, 2019

from pymtl import *

class Network( Component ):
  def construct( s, PacketType, PositionType, RouterType, ChannelType, 
                 SendIfcType, RecvIfcType, num_routers, num_terminals, 
                 num_channels, channel_latency = 0 ):

    # Constants

    s.num_routers = num_routers

    # Interface

    s.recv       = [ RecvIfcType(PacketType) for _ in range(num_terminals)]
    s.send       = [ SendIfcType(PacketType) for _ in range(num_terminals)]

    # Components

    s.routers    = [ RouterType( PacketType, PositionType ) 
                     for i in range( s.num_routers ) ]

    s.channels   = [ ChannelType( PacketType, latency = channel_latency)
                     for _ in range( num_channels ) ]

  def line_trace( s ):
    trace = [ "" for _ in range( s.num_routers ) ]
    for i in range( s.num_routers ):
      trace[i] = "{}".format( s.routers[i].recv )
    return "|".join( trace )
