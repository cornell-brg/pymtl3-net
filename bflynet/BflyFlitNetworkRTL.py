#=========================================================================
# BfNetworkRTL.py
#=========================================================================
# Butterfly network implementation.
#
# Author : Cheng Tan
#   Date : April 6, 2019

from pymtl3             import *
from BflyRouterRTL      import BflyRouterRTL
from BflyFlitRouterRTL  import BflyFlitRouterRTL
from channel.ChannelRTL import ChannelRTL
from pymtl3.stdlib.ifcs.SendRecvIfc  import *
from ocn_pclib.ifcs.PhysicalDimension import PhysicalDimension

class BflyFlitNetworkRTL( Component ):
  def construct( s, PacketType, PositionType, k_ary, n_fly, chl_lat=0 ):

    # Constants

    s.dim = PhysicalDimension()
    s.k_ary = k_ary
    s.n_fly = n_fly
    s.r_rows        = k_ary ** ( n_fly - 1 )
    s.num_routers = n_fly * ( s.r_rows )
    s.num_terminals = k_ary ** n_fly
    num_channels  = ( n_fly - 1 ) * ( s.r_rows ) * k_ary
    #FIXME: only used for translation 4-ary, 3-fly
#    num_critical = 48

    # Interface

    s.recv = [ RecvIfcRTL(PacketType) for _ in range(s.num_terminals)]
    s.send = [ SendIfcRTL(PacketType) for _ in range(s.num_terminals)]

    # Components

    s.routers  = [ BflyFlitRouterRTL( PacketType, PositionType )
                   for i in range( s.num_routers ) ]

#    s.channels_critical = [ ChannelRTL( PacketType, latency = 1)
#                          for _ in range( num_critical ) ]
#
#    s.channels_normal   = [ ChannelRTL( PacketType, latency = chl_lat)
#                          for _ in range( num_channels - num_critical) ]
    s.channels = [ ChannelRTL( PacketType, latency = chl_lat )
                 for _ in range( num_channels) ]


#    s.pos      = [[ PositionType( r, n ) for r in range( s.r_rows )]
#                    for n in range( n_fly )]
    s.pos      = [ PositionType( r%s.r_rows, r/s.r_rows )
                 for r in range( s.num_routers )]

    # Connect s.routers together in Butterfly

    for r in range( s.num_routers ):
      s.connect( s.routers[r].pos.row,   s.pos[r].row   )
      s.connect( s.routers[r].pos.stage, s.pos[r].stage )

    chl_id = 0
#    chl_normal_id = 0
#    chl_critical_id = 0
    terminal_id_recv = 0
    terminal_id_send = 0
    group_size = s.r_rows
  
    for f in range( n_fly - 1 ):
      num_group  = s.r_rows / group_size
      for g in range( num_group ):
        for gs in range( group_size ):
          for k in range( k_ary ):
            index = g * group_size + gs
            base  = g * group_size
            interval = group_size/k_ary * k
#            s.connect( s.routers[f*s.r_rows+index].\
#                    send[(k+gs/(group_size/k_ary))%k_ary],
#                       s.channels[chl_id].recv )
#            s.connect( s.channels[chl_id].send,
#                       s.routers[(f+1)*s.r_rows+base+(gs+interval)%group_size].\
#                               recv[k] )
            # record the critical channel
            router_left = f*s.r_rows+index
            router_right = (f+1)*s.r_rows+base+(gs+interval)%group_size
            group_left    = router_left  % s.r_rows
            group_right   = router_right % s.r_rows
            group_left_x  = group_left  % k_ary
            group_right_x = group_right % k_ary
            group_left_y  = group_left  / k_ary
            group_right_y = group_right / k_ary
#            if abs( group_left_x - group_right_x ) >= k_ary/2 or\
#               abs( group_left_y - group_right_y ) >= k_ary/2:
#              print chl_id
            s.connect( s.routers[f*s.r_rows+index].\
                    send[(k+gs/(group_size/k_ary))%k_ary],
                       s.channels[chl_id].recv )
            s.connect( s.channels[chl_id].send,
                       s.routers[(f+1)*s.r_rows+base+(gs+interval)%group_size].\
                               recv[k] )
#              chl_critical_id += 1
#            else:
#              s.connect( s.routers[f*s.r_rows+index].\
#                      send[(k+gs/(group_size/k_ary))%k_ary],
#                         s.channels_normal[chl_normal_id].recv )
#              s.connect( s.channels_normal[chl_normal_id].send,
#                         s.routers[(f+1)*s.r_rows+base+(gs+interval)%group_size].\
#                                 recv[k] )
#              chl_normal_id += 1

            chl_id += 1
      group_size = group_size / k_ary

    # Connect the router ports with Network Interfaces
    for i in range( s.num_routers ):
      if i < s.r_rows:
        for j in range( k_ary ):
          s.connect(s.recv[terminal_id_recv], s.routers[i].recv[j])
          terminal_id_recv += 1

      if i >= s.num_routers - s.r_rows:
        for j in range( k_ary ):
          s.connect(s.send[terminal_id_send], s.routers[i].send[j])
          terminal_id_send += 1

#    # FIXME: unable to connect a struct to a port.
#    @s.update
#    def up_pos():
#      for n in range( n_fly ):
#        for r in range( s.r_rows ):
#          s.routers[s.r_rows * n + r].pos = s.pos[n][r]

  def line_trace( s ):
    trace = [ "" for _ in range( s.num_terminals ) ]
    for i in range( s.num_terminals ):
      trace[i] += s.send[i].line_trace()
    return "|".join( trace )

  def elaborate_physical( s ):

    # FIXME: This should be done by the pass (but not yet merged into master...)
    for r in s.routers:
      r.elaborate_physical()
#    for c in s.channels:
#      c.elaborate_physical()

    BOUNDARY = 500
    INTERVAL_MINOR = 20
    INTER_ROUTER = 1000
#    GROUP_LEN = 400
    router_length = s.routers[0].dim.w
    router_height = s.routers[0].dim.h
#    link_length = s.channels[0].dim.w

    print 'setPlaceMode -hardFence  true'
    print 'setCTSMode   -honorFence true'
    print 'setOptMode   -honorFence true'
    MAX_X = 0
    MAX_Y = 0

    for row in range( s.r_rows ):
      for f in range( s.n_fly ):
        r = s.routers[ row + f * s.r_rows ]
#        r.dim.x = BOUNDARY + row%s.k_ary * (GROUP_LEN + \
#                  INTER_ROUTER) + GROUP_LEN
#        r.dim.y = BOUNDARY + (s.r_rows/s.k_ary - 1 - row/s.k_ary) * \
#                  (GROUP_LEN + INTER_ROUTER) + GROUP_LEN

        r.dim.x = BOUNDARY + row%s.k_ary * (s.n_fly*router_length + \
                  INTER_ROUTER + (s.n_fly-1)*INTERVAL_MINOR) + \
                  f * (router_length + INTERVAL_MINOR )
        r.dim.y = BOUNDARY + (s.r_rows/s.k_ary - 1 - row/s.k_ary) * \
                  (router_height + INTER_ROUTER)
        print 'createFence routers___{}  {}  {}  {}  {}'.\
              format( row+f*s.r_rows, r.dim.x, r.dim.y,\
                      r.dim.x+router_length, r.dim.y+router_height )

        if r.dim.x+router_length > MAX_X:
          MAX_X = r.dim.x + router_length

        if r.dim.y+router_height > MAX_Y:
          MAX_Y = r.dim.y + router_height
#        print 'router[{}].dim: ({},{}); pos: {}'.\
#              format( row+f*s.r_rows, r.dim.x, r.dim.y, r.pos )

    print 'size: {},{}'.format( MAX_X + BOUNDARY, MAX_Y + BOUNDARY )


  def elaborate_logical( s ):
    link_length = s.channels[0].dim.w

    for i, r in enumerate( s.routers ):
      r.dim.x = i / s.r_rows * ( r.dim.w + link_length )
      r.dim.y = i % s.r_rows * ( r.dim.h + link_length )

    s.dim.w = s.r_rows * ( r.dim.w + link_length )
    s.dim.h = s.r_rows * ( r.dim.h + link_length )
