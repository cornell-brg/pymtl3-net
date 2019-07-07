#=========================================================================
# BfNetworkRTL.py
#=========================================================================
# Butterfly network implementation.
#
# Author : Cheng Tan
#   Date : April 6, 2019

from pymtl3             import *
from channel.ChannelRTL import ChannelRTL
from pymtl3.stdlib.ifcs.SendRecvIfc  import *

class ChannelNetworkRTL( Component ):
  def construct( s, PacketType, PositionType, k_ary, n_fly, chl_lat=0 ):

    # Constants
    s.num_chl = k_ary * n_fly 

    # Interface

    s.recvxx = [ RecvIfcRTL(PacketType) for _ in range(s.num_chl)]
    s.sendxx = [ SendIfcRTL(PacketType) for _ in range(s.num_chl)]

    # Components

    s.channels = [ ChannelRTL( PacketType, latency = chl_lat)
                 for _ in range( s.num_chl ) ]

    # Connect s.routers together in Butterfly
    for i in range( s.num_chl ):
      s.connect( s.recvxx[i], s.channels[i].recv )
      s.connect( s.sendxx[i], s.channels[i].send )

  def line_trace( s ):
    trace = [ "" for _ in range( s.num_chl ) ]
    for i in range( s.num_chl ):
      trace[i] += s.sendxx[i].line_trace()
    return "|".join( trace )

