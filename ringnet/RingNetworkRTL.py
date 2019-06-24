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
    # trace = [ "" for _ in range( s.num_routers ) ]
    # for i in range( s.num_routers ):
    #   # trace[i] += s.send[i].line_trace()
    #   for j in range( 3 ):
    #     trace[i] += "({},{},{},{})".format(
    #       s.routers[i].input_units[j].buffers[0].count,
    #       s.routers[i].input_units[j].buffers[1].count,
    #       s.routers[i].input_units[j].give.msg,
    #       s.routers[i].route_units[j].give[1].msg,
    #     )
    #     trace[i] += (
    #       "S:"+
    #       "|".join( [ str( s.routers[i].switch_units[j].get[x].msg )  for x in range(3) ] )+
    #       "<{}>".format( ",".join([ str( s.routers[i].switch_units[j].get[x].rdy )  for x in range(3) ]) )+
    #       "[R:{}:G:{}]".format( str( s.routers[i].switch_units[j].arbiter.reqs ), str( s.routers[i].switch_units[j].arbiter.grants ) )+
    #       ">"+str( s.routers[i].switch_units[j].give.msg )
    #     )
    #     trace[i] += "A:"+str( s.routers[i].input_units[j].arbiter.reqs)
    #     trace[i] += "G:"+str( s.routers[i].input_units[j].arbiter.grants )
    #     trace[i] += "E:"+str( s.routers[i].input_units[j].encoder.out ) + ">"
    #     trace[i] += "m:"+str( s.routers[i].output_units[j].get.msg) + " I "
    #     trace[i] += "r:"+str( s.routers[i].output_units[j].get.rdy) + " I "
    #     trace[i] += str( s.routers[i].output_units[j].line_trace() )
    #   trace[i] +=" >>> "
    #  Input unit and route unit
    in_trace = [ "" for _ in range( s.num_routers ) ]
    for i in range ( s.num_routers ):
      in_trace[i] += str(s.recv[i])
      for j in range( 3 ):
        in_trace[i] += "IU{}{{".format( j )
        in_trace[i] += "({},{})".format( s.routers[i].input_units[j].buffers[0].count, s.routers[i].input_units[j].buffers[1].count )
        in_trace[i] += ">{}}}".format( s.routers[i].input_units[j].give.msg )
        in_trace[i] += "RU{}{{".format( j )
        in_trace[i] += "|".join([ "{}r{}".format( s.routers[i].route_units[j].give[x].msg, s.routers[i].route_units[j].give[x].rdy ) for x in range(3) ])
        in_trace[i] += "}}"

    # Switch unit and output unit
    out_trace = [ "" for _ in range( s.num_routers ) ]
    for i in range( s.num_routers ):
      for j in range( 3 ):
        out_trace[i] += "SU{}{{".format( j )
        out_trace[i] += "|".join([ "{}r{}".format( s.routers[i].switch_units[j].get[x].msg, s.routers[i].switch_units[j].get[x].rdy ) ])
        out_trace[i] += "}}"
        out_trace[i] += "OU{}{{".format( j )
        out_trace[i] += "({}r{})".format( s.routers[i].output_units[j].get.msg, s.routers[i].output_units[j].get.rdy )
      out_trace[i] += str(s.send[i])
    # Assemble line trace
    in_str  = " | ".join( in_trace )
    out_str = " | ".join( out_trace )
    return  "{} XXX {}".format( in_str, out_str )
