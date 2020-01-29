"""
=========================================================================
BfNetworkRTL.py
=========================================================================
RTL implementation of a butterfly network.

Author : Cheng Tan
  Date : April 6, 2019
"""
from channel.ChannelRTL import ChannelRTL
from ocnlib.ifcs.PhysicalDimension import PhysicalDimension
from pymtl3 import *
from pymtl3.stdlib.ifcs.SendRecvIfc import *

from .BflyRouterRTL import BflyRouterRTL


class BflyNetworkRTL( Component ):

  def construct( s, PacketType, PositionType, k_ary, n_fly, chl_lat=0 ):

    # Constants

    s.dim           = PhysicalDimension()
    s.k_ary         = k_ary
    s.n_fly         = n_fly
    s.r_rows        = k_ary ** ( n_fly - 1 )
    s.num_routers   = n_fly * ( s.r_rows )
    s.num_terminals = k_ary ** n_fly
    num_channels    = ( n_fly - 1 ) * ( s.r_rows ) * k_ary

    # Interface

    s.recv = [ RecvIfcRTL(PacketType) for _ in range(s.num_terminals)]
    s.send = [ SendIfcRTL(PacketType) for _ in range(s.num_terminals)]

    # Components

    s.routers  = [ BflyRouterRTL( PacketType, PositionType, k_ary, n_fly )
                   for i in range( s.num_routers ) ]

    s.channels = [ ChannelRTL( PacketType, latency = chl_lat )
                 for _ in range( num_channels) ]

    s.pos      = [ PositionType( r%s.r_rows, r//s.r_rows )
                 for r in range( s.num_routers )]

    # Connect routers together in Butterfly

    for r in range( s.num_routers ):
      s.routers[r].pos.row   //= s.pos[r].row
      s.routers[r].pos.stage //= s.pos[r].stage

    chl_id = 0
    terminal_id_recv = 0
    terminal_id_send = 0
    group_size = s.r_rows

    for f in range( n_fly - 1 ):
      num_group  = s.r_rows // group_size
      for g in range( num_group ):
        for gs in range( group_size ):
          for k in range( k_ary ):
            index = g * group_size + gs
            base  = g * group_size
            interval = group_size // k_ary * k

            router_left   = f*s.r_rows+index
            router_right  = (f+1)*s.r_rows+base+(gs+interval)%group_size
            group_left    = router_left  % s.r_rows
            group_right   = router_right % s.r_rows
            group_left_x  = group_left   % k_ary
            group_right_x = group_right  % k_ary
            group_left_y  = group_left  // k_ary
            group_right_y = group_right // k_ary

            rtr_idx   = f * s.r_rows + index
            ifc_tdx   = ( k + gs // (group_size//k_ary) ) % k_ary
            rtr_idx_n = (f+1)*s.r_rows+base+(gs+interval)%group_size

            s.routers[rtr_idx].send[ifc_tdx] //= s.channels[chl_id].recv
            s.channels[chl_id].send          //= s.routers[rtr_idx_n].recv[k]

            chl_id += 1
      group_size = group_size // k_ary

    # Connect the router ports with Network Interfaces

    for i in range( s.num_routers ):
      if i < s.r_rows:
        for j in range( k_ary ):
          s.recv[terminal_id_recv] //= s.routers[i].recv[j]
          terminal_id_recv += 1

      if i >= s.num_routers - s.r_rows:
        for j in range( k_ary ):
          s.send[terminal_id_send] //= s.routers[i].send[j]
          terminal_id_send += 1

  def line_trace( s ):
      send_lst = []
      recv_lst = []
      for r in s.routers:
        has_recv = any([ r.recv[i].en for i in range(s.k_ary) ])
        has_send = any([ r.send[i].en for i in range(s.k_ary) ])
        if has_send:
          send_lst.append( f'{r.pos}' )
        if has_recv:
          recv_lst.append( f'{r.pos}')
      send_str = ','.join( send_lst )
      recv_str = ','.join( recv_lst )
      return f' {send_str:2} -> {recv_str:2}'

  def elaborate_physical( s ):

    for r in s.routers:
      r.elaborate_physical()

    BOUNDARY = 500
    INTERVAL_MINOR = 20
    INTER_ROUTER = 1000

    router_length = s.routers[0].dim.w
    router_height = s.routers[0].dim.h

    print( 'setPlaceMode -hardFence  true' )
    print( 'setCTSMode   -honorFence true' )
    print( 'setOptMode   -honorFence true' )
    MAX_X = 0
    MAX_Y = 0

    for row in range( s.r_rows ):
      for f in range( s.n_fly ):
        r = s.routers[ row + f * s.r_rows ]

        r.dim.x = BOUNDARY + row%s.k_ary * (s.n_fly*router_length + \
                  INTER_ROUTER + (s.n_fly-1)*INTERVAL_MINOR) + \
                  f * (router_length + INTERVAL_MINOR )
        r.dim.y = BOUNDARY + (s.r_rows//s.k_ary - 1 - row//s.k_ary) * \
                  (router_height + INTER_ROUTER)
        print( 'createFence routers___{}  {}  {}  {}  {}'.\
              format( row+f*s.r_rows, r.dim.x, r.dim.y,\
                      r.dim.x+router_length, r.dim.y+router_height ))

        if r.dim.x+router_length > MAX_X:
          MAX_X = r.dim.x + router_length

        if r.dim.y+router_height > MAX_Y:
          MAX_Y = r.dim.y + router_height

    print( 'size: {},{}'.format( MAX_X + BOUNDARY, MAX_Y + BOUNDARY ) )

  def elaborate_logical( s ):
    link_length = s.channels[0].dim.w

    for i, r in enumerate( s.routers ):
      r.dim.x = i // s.r_rows * ( r.dim.w + link_length )
      r.dim.y = i %  s.r_rows * ( r.dim.h + link_length )

    s.dim.w = s.r_rows * ( r.dim.w + link_length )
    s.dim.h = s.r_rows * ( r.dim.h + link_length )
