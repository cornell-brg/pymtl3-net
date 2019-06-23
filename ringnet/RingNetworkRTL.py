"""
=========================================================================
RingNetworkRTL.py
=========================================================================
Ring network implementation.

Author : Yanghui Ou, Cheng Tan
  Date : June 22, 2019
"""
from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL

from directions import *
from RingRouterRTL import RingRouterRTL
from ocn_pclib.ifcs.CreditIfc import RecvRTL2CreditSendRTL, CreditRecvRTL2SendRTL

class RingNetworkRTL( Component ):

  def construct( s,
    PacketType,
    PositionType,
    num_routers=4,
    chl_lat=0,
    nvcs=2,
    credit_line=2,
   ):

    # Constants
    s.num_routers = num_routers

    # Interface
    s.recv = [ RecvIfcRTL(PacketType) for _ in range(s.num_routers)]
    s.send = [ SendIfcRTL(PacketType) for _ in range(s.num_routers)]

    # Components
    s.routers    = [ RingRouterRTL( PacketType, PositionType )
                     for i in range( s.num_routers ) ]

    s.recv_adapters = [ RecvRTL2CreditSendRTL( PacketType, nvcs=nvcs, credit_line=credit_line )
                        for _ in range( s.num_routers ) ]
    s.send_adapters = [ CreditRecvRTL2SendRTL( PacketType, nvcs=nvcs, credit_line=credit_line )
                        for _ in range( s.num_routers ) ]

    # Connect s.routers together in ring

    for i in range( s.num_routers ):
      next_id = (i+1) % num_routers
      s.connect( s.routers[i].send[RIGHT],      s.routers[next_id].recv[LEFT] )
      s.connect( s.routers[next_id].send[LEFT], s.routers[i].recv[RIGHT]      )

      # Connect the self port (with Network Interface)

      s.connect( s.recv[i],               s.recv_adapters[i].recv )
      s.connect( s.recv_adapters[i].send, s.routers[i].recv[SELF] )

      s.connect( s.routers[i].send[SELF], s.send_adapters[i].recv )
      s.connect( s.send_adapters[i].send, s.send[i]               )

    # FIXME: unable to connect a struct to a port.
    @s.update
    def up_pos():
      for r in range( s.num_routers ):
        s.routers[r].pos = PositionType( r )

  def line_trace( s ):
    trace = [ "" for _ in range( s.num_routers ) ]
    for i in range( s.num_routers ):
      trace[i] += s.send[i].line_trace()
    return "|".join( trace )
