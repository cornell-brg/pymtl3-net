#=========================================================================
# BfNetworkRTL.py
#=========================================================================
# Butterfly network implementation.
#
# Author : Cheng Tan
#   Date : April 6, 2019

from pymtl                  import *
from pclib.ifcs.SendRecvIfc import *
from channel.ChannelRTL     import ChannelRTL
from BflyRouterRTL          import BflyRouterRTL

class BflyNetworkRTL( Component ):
  def construct( s, PacketType, PositionType, k_ary, n_fly, chl_lat=0 ):

    # Constants

    r_rows        = k_ary ** ( n_fly - 1 )
    s.num_routers = n_fly * ( r_rows )
    s.num_terminals = k_ary ** n_fly
    num_channels  = ( n_fly - 1 ) * ( r_rows ) * k_ary

    # Interface

    s.recv = [ RecvIfcRTL(PacketType) for _ in range(s.num_terminals)]
    s.send = [ SendIfcRTL(PacketType) for _ in range(s.num_terminals)]

    # Components

    s.routers  = [ BflyRouterRTL( PacketType, PositionType )
                   for i in range( s.num_routers ) ]

    s.channels = [ ChannelRTL( PacketType, latency = chl_lat)
                     for _ in range( num_channels ) ]

    # Connect s.routers together in Butterfly

    chl_id = 0
    terminal_id_recv = 0
    terminal_id_send = 0
    for i in range( s.num_routers ):
      if i < s.num_routers - r_rows:
        for j in range( k_ary ):
          s.connect( s.routers[i].send[j],    s.channels[chl_id].recv       )

          # FIXME: Utilize bit to index the specific router.
          s.connect( s.channels[chl_id].send, 
                     s.routers[(i/r_rows+1)*r_rows+(i%k_ary+j
                         *(r_rows/k_ary))%r_rows].recv[i%k_ary] )
          chl_id += 1

      # Connect the ports with Network Interfaces
      if i < r_rows:
        for j in range( k_ary ):
          s.connect(s.recv[terminal_id_recv], s.routers[i].recv[j])
          terminal_id_recv += 1

      if i >= s.num_routers - r_rows:
        for j in range( k_ary ):
          s.connect(s.send[terminal_id_send], s.routers[i].send[j])
          terminal_id_send += 1

    # FIXME: unable to connect a struct to a port.
    @s.update
    def up_pos():
      for n in range( n_fly ):
        for r in range( r_rows ):
          s.routers[r_rows * n + r].pos = PositionType( r, n )

  def line_trace( s ):
    trace = [ "" for _ in range( s.num_terminals ) ]
    for i in range( s.num_terminals ):
      trace[i] += s.send[i].line_trace()
    return "|".join( trace )