#=========================================================================
# BfNetworkRTL.py
#=========================================================================
# Butterfly network implementation.
#
# Author : Cheng Tan
#   Date : April 6, 2019

from pymtl                      import *
from network.Network            import Network
from pclib.ifcs.SendRecvIfc     import *
from channel.ChannelRTL         import ChannelRTL
from bfnet.bfrouter.BfRouterRTL import BfRouterRTL

class BfNetworkRTL( Network ):
  def construct( s, PacketType, PositionType, k_ary, n_fly, chl_lat=0 ):

    # Constants

    n_rows            = k_ary ** ( n_fly - 1 )
    s.num_routers     = n_fly * ( n_rows )
    num_terminals   = k_ary * n_rows
    num_channels      = ( n_fly - 1 ) * ( n_rows ) * k_ary

    # Interface

    s.recv = [ RecvIfcRTL(PacketType) for _ in range(num_terminals)]
    s.send = [ SendIfcRTL(PacketType) for _ in range(num_terminals)]

    # Components

    s.routers  = [ BfRouterRTL( PacketType, PositionType, k_ary = k_ary )
                     for i in range( s.num_routers ) ]
    s.channels = [ ChannelRTL( PacketType, latency = chl_lat)
                     for _ in range( num_channels ) ]


    # Connect s.routers together in Mesh

    chl_id = 0
    terminal_id_recv = 0
    terminal_id_send = 0
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
