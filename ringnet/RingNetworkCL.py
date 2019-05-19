#=========================================================================
# RingNetworkCL.py
#=========================================================================
# Cycle level ring network implementation.
#
# Author : Yanghui Ou
#   Date : May 19, 2019

from pymtl import *
from directions import *
from RingRouterCL import RingRouterCL
from channel.ChannelCL import ChannelCL
from pclib.ifcs.GuardedIfc import (
  GuardedCallerIfc,
  GuardedCalleeIfc,
  guarded_ifc
)

class RingNetworkCL( Component ):
  def construct( s, PacketType, PositionType, nrouters=4, chl_lat=0 ):

    # Constants

    s.nrouters = nrouters
    num_channels  = nrouters * 2
    s.num_terminals = nrouters

    # Interface

    s.recv       = [ GuardedCalleeIfc() for _ in range(s.num_terminals) ]
    s.send       = [ GuardedCallerIfc() for _ in range(s.num_terminals) ]

    # Components

    s.routers    = [ RingRouterCL( PacketType, PositionType )
                     for i in range( s.nrouters ) ]

    s.channels   = [ ChannelCL( PacketType, latency = chl_lat)
                     for _ in range( num_channels ) ]

    # Connect s.routers together in Mesh

    chl_id = 0
    for i in range( s.nrouters ):
      s.connect( s.routers[i].send[RIGHT], s.channels[chl_id].recv                   )
      s.connect( s.channels[chl_id].send,  s.routers[(i+1)%nrouters].recv[LEFT] )
      chl_id += 1

      s.connect( s.routers[(i+1)%nrouters].send[LEFT], s.channels[chl_id].recv  )
      s.connect( s.channels[chl_id].send,                 s.routers[i].recv[RIGHT] )
      chl_id += 1

      # Connect the self port (with Network Interface)

      s.connect(s.recv[i], s.routers[i].recv[SELF])
      s.connect(s.send[i], s.routers[i].send[SELF])

    # FIXME: unable to connect a struct to a port.
    @s.update
    def up_pos():
      for r in range( s.nrouters ):
        s.routers[r].pos = PositionType( r )

  def line_trace( s ):
    return "|".join( 
      [ s.routers[i].line_trace() for i in range( s.num_terminals ) ] 
    )
