#=========================================================================
# RouteRTL.py
#=========================================================================
# Simple network-on-chip router, try to connect all the units together
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 8, 2019

from pymtl import *
from pclib.ifcs.EnRdyIfc import InEnRdyIfc, OutEnRdyIfc
from src.router.Router   import Router

class RouterRTL( RTLComponent, Router ):
  def construct( s, PacketType, PositionType, num_inports, num_outports, 
          InputUnitType, RouteUnitType, SwitchUnitType, OutputUnitType ):
    
    super(RouterRTL, s).__construct__( PacketType, PositionType, num_inports, 
num_outports, InputUnitType, RouteUnitType, SwitchUnitType, OutputUnitType )

    # Interface
    s.recv  = [  InEnRdyIfc( PacketType ) for _ in range( s.num_inports  ) ]
    s.send  = [ OutEnRdyIfc( PacketType ) for _ in range( s.num_outports ) ]

    s.pos   = InVPort( PositionType )

    # Connections
    for i in range( s.num_inports ):
      s.connect( s.recv[i],             s.input_units[i].recv    )
      s.connect( s.input_units[i].send, s.route_units[i].recv    )
      s.connect( s.pos,                 s.route_units[i].pos     )

    for i in range( s.num_inports ):
      for j in range( s.num_outports ):
        s.connect( s.route_units[i].send[j], s.switch_units[j].recv[i] )

    for j in range( s.num_outports ):
      s.connect( s.switch_units[j].send, s.output_units[j].recv )
      s.connect( s.output_units[j].send, s.send[j]        )

  def line_trace( s ):
    tmp_str = "({},{}):".format( s.pos.pos_x, s.pos.pos_y )
    out_str = [ "" for _ in range( s.num_inports ) ]
    for i in range (s.num_inports):
      out_str[i] = " {}->({},{})".format( i, s.recv[i].msg.dst_x, s.recv[i].msg.dst_y )
      tmp_str += out_str[i]
    tmp_str += ' recv.rdy:<'
    for i in range (s.num_inports):
      tmp_str += "{}".format(int(s.input_units[i].recv.rdy))
    tmp_str += '> send.en:<'
    for i in range (s.num_outports):
      tmp_str += "{}".format(s.send[i].en)
    tmp_str += ">"
    return tmp_str
