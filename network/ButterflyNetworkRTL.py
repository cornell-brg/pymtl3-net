#=========================================================================
# ButterflyNetworkRTL.py
#=========================================================================
# Butterfly network implementation.
#
# Author : Cheng Tan
#   Date : April 6, 2019

from pymtl                           import *
from pclib.ifcs.SendRecvIfc          import *
from router.ButterflyRouterRTL       import ButterflyRouterRTL
from router.InputUnitRTL             import InputUnitRTL
from router.DTRButterflyRouteUnitRTL import DTRButterflyRouteUnitRTL
from router.SwitchUnitRTL            import SwitchUnitRTL
from router.OutputUnitRTL            import OutputUnitRTL
from channel.ChannelRTL              import ChannelRTL

class ButterflyNetworkRTL( Component ):
  def construct( s, PacketType, PositionType, k_ary, n_fly, channel_latency=0 ):
    # Constants

    n_rows            = k_ary ** ( n_fly - 1 )
    s.num_routers     = n_fly * ( n_rows )
    s.num_terminals   = k_ary * n_rows
    num_channels      = ( n_fly - 1 ) * ( n_rows ) * k_ary
    s.channel_latency = 0

    RouteUnitType     = DTRButterflyRouteUnitRTL

    # Interface
    s.recv       = [ RecvIfcRTL(PacketType) for _ in range(s.num_terminals)]
    s.send       = [ SendIfcRTL(PacketType) for _ in range(s.num_terminals)]

    # Components
    s.routers    = [ ButterflyRouterRTL( PacketType, PositionType, RouteUnitType,
                     k_ary ) for i in range(s.num_routers)]

    s.channels   = [ ChannelRTL(PacketType, latency=channel_latency)
                     for _ in range( num_channels ) ]

    chl_id = 0
    terminal_id_recv = 0
    terminal_id_send = 0

    # Connect s.routers together in Mesh
    for i in range( s.num_routers ):
      if i < s.num_routers - n_rows:
        for j in range( k_ary ):
          s.connect( s.routers[i].send[j],    s.channels[chl_id].recv       )

          # FIXME: Utilize bit to index the specific router.
          s.connect( s.channels[chl_id].send, 
                     s.routers[(i/n_rows+1)*n_rows+(i%k_ary+j
                         *(n_rows/k_ary))%n_rows].recv[i%k_ary] )
          chl_id += 1

      # Connect the ports with Network Interfaces
      if i < n_rows:
        for j in range( k_ary ):
          s.connect(s.recv[terminal_id_recv], s.routers[i].recv[j])
          terminal_id_recv += 1

      if i >= s.num_routers - n_rows:
        for j in range( k_ary ):
          s.connect(s.send[terminal_id_send], s.routers[i].send[j])
          terminal_id_send += 1

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
