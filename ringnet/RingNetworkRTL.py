"""
=========================================================================
RingNetworkRTL.py
=========================================================================
Ring network implementation.

Author : Yanghui Ou, Cheng Tan
  Date : June 22, 2019
"""
from ocn_pclib.ifcs.CreditIfc import (CreditRecvRTL2SendRTL,
                                      RecvRTL2CreditSendRTL)
from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL

from .directions import *
from .RingRouterRTL import RingRouterRTL


class RingNetworkRTL( Component ):

  def construct( s,
    PacketType,
    PositionType,
    num_routers=4,
    chl_lat=0,
    vc=2,
    credit_line=2,
   ):

    # Constants
    s.num_routers = num_routers
#    IDType = mk_bits(clogs(num_routers))

    # Interface
    s.recv = [ RecvIfcRTL(PacketType) for _ in range(s.num_routers)]
    s.send = [ SendIfcRTL(PacketType) for _ in range(s.num_routers)]

    # Components
    s.routers = [ RingRouterRTL( PacketType, PositionType, num_routers, vc=vc )
                     for i in range( num_routers ) ]

    s.recv_adp = [ RecvRTL2CreditSendRTL( PacketType, vc=vc, credit_line=credit_line )
                        for _ in range( num_routers ) ]
    s.send_adp = [ CreditRecvRTL2SendRTL( PacketType, vc=vc, credit_line=credit_line )
                        for _ in range( num_routers ) ]

    # Connect s.routers together in ring

    for i in range( s.num_routers ):
      next_id = (i+1) % num_routers
      s.routers[i].send[RIGHT]      //= s.routers[next_id].recv[LEFT]
      s.routers[next_id].send[LEFT] //= s.routers[i].recv[RIGHT]
      # Connect the self port (with Network Interface)
      s.recv[i]                     //= s.recv_adp[i].recv
      s.recv_adp[i].send            //= s.routers[i].recv[SELF]
      s.routers[i].send[SELF]       //= s.send_adp[i].recv
      s.send_adp[i].send            //= s.send[i]

    @s.update
    def up_pos():
      for r in range( s.num_routers ):
        s.routers[r].pos = PositionType( r )

  def line_trace( s, level='1pkt' ):

    # Verbose line trace
    if level == 'verbose':
      #  Input unit and route unit
      in_trace = [ "" for _ in range( s.num_routers ) ]
      for i in range ( s.num_routers ):
        in_trace[i] += str(s.recv[i])
        for j in range( 3 ):
          in_trace[i] += "IU{}{{".format( j )
          in_trace[i] += "({},{})".format( s.routers[i].input_units[j].buffers[0].count, s.routers[i].input_units[j].buffers[1].count )
          in_trace[i] += ">{}}}".format( "|".join( [ str(s.routers[i].input_units[j].give[x].msg) for x in range(2)] ) )
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
          out_trace[i] += "<{},{}>".format( s.routers[i].output_units[j].credit[0].count, s.routers[i].output_units[j].credit[1].count )
        out_trace[i] += str(s.send[i])
      # Assemble line trace
      in_str  = " | ".join( in_trace )
      out_str = " | ".join( out_trace )
      return  " >>>>> ".join( [ "{} __XX__ {}".format( in_trace[i], out_trace[i] ) for i in range(s.num_routers)] )

    # Simple line trace
    elif level=='simple':
      in_trace  = [ str(s.recv[i]) for i in range( s.num_routers) ]
      out_trace = [ str(s.send[i]) for i in range( s.num_routers) ]
      in_str = "|".join( in_trace )
      out_str = "|".join( out_trace )
      return "{}(){}".format( in_str, out_str )

    else:
      send_lst = []
      recv_lst = []
      for r in s.routers:
        has_recv = any([ r.recv[i].en for i in range(3) ])
        has_send = any([ r.send[i].en for i in range(3) ])
        if has_send:
          send_lst.append( f'{r.pos}' )
        if has_recv:
          recv_lst.append( f'{r.pos}')
      send_str = ','.join( send_lst )
      recv_str = ','.join( recv_lst )
      return f' {send_str:2} -> {recv_str:2}'
