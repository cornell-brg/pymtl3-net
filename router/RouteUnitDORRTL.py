#=========================================================================
# RouteUnitDORRTL.py
#=========================================================================
# A route unit with configurable routing strategies.
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 2, 2019

from pymtl import *
from pclib.ifcs.EnRdyIfc  import InEnRdyIfc, OutEnRdyIfc

from Packet import Packet

class RouteUnitDORRTL( RTLComponent ):
#  def __init__( s, msg_type, dimension ):
#  def construct( s, msg_type, routing_strategy, num_outports ):
  def construct( s, dimension, num_outports, pos_x, pos_y):

    # Constants 
    s.num_outports = num_outports

    s.x_addr_nbits = 4
    s.y_addr_nbits = 4
    NORTH = 0
    SOUTH = 1
    WEST  = 2
    EAST  = 3
    SELF  = 4

    # Interface
    s.recv = InEnRdyIfc( Packet )
    s.send = [ OutEnRdyIfc (Packet) for _ in range ( s.num_outports ) ]

#    s.pos_x = InPort( s.x_addr_nbits )
#    s.pos_y = InPort( s.y_addr_nbits )
    s.pos_x = pos_x
    s.pos_y = pos_y

    # Componets
#    s.out_rdys = Wire( s.num_outports )
#    s.src_x = Wire( s.x_addr_nbits )
    s.src_x = Wire( Bits4 )
    s.src_y = Wire( Bits4 )
#    s.dst_x = Wire( Bits4 )
#    s.dst_y = Wire( Bits4 )

    s.out_rdys = Wire( mk_bits( s.num_outports ) )

    s.pkt     = Wire( Packet )
    s.out_dir = 'N'

    # Connections
    s.connect( s.pkt,         s.recv.msg    )
    for i in range( s.num_outports ):
      s.connect( s.recv.msg,    s.send[i].msg )
      s.connect( s.out_rdys[i], s.send[i].rdy )
   
    # Routing logic
    @s.update
    def routingLogic():
      if dimension.lower() == 'x':
        for i in range( s.num_outports ):
          s.send[i].en = 0
        if s.pos_x == s.pkt.dst_x and s.pos_y == s.pkt.dst_y:
          s.send[SELF].en  = s.recv.en
          s.out_dir = 'C'
        elif s.pkt.dst_x < s.pos_x:
          s.send[NORTH].en = s.recv.en
          s.out_dir = 'N'
        elif s.pkt.dst_x > s.pos_x:
          s.send[SOUTH].en = s.recv.en
          s.out_dir = 'S'
        elif s.pkt.dst_y < s.pos_y:
          s.send[WEST].en  = s.recv.en
          s.out_dir = 'W'
        else:
          s.send[EAST].en  = s.recv.en
          s.out_dir = 'E'

      elif dimension.lower() == 'y':
        for i in range( s.num_outports ):
          s.send[i].en = 0
        if s.pos_x == s.pkt.dst_x and s.pos_y == s.pkt.dst_y:
          s.send[SELF].en  = s.recv.en
          s.out_dir = 'C'
        elif s.pkt.dst_y < s.pos_y:
          s.send[WEST].en = s.recv.en
          s.out_dir = 'W'
        elif s.pkt.dst_y > s.pos_y:
          s.send[EAST].en = s.recv.en
          s.out_dir = 'E'
        elif s.pkt.dst_x < s.pos_x:
          s.send[NORTH].en = s.recv.en
          s.out_dir = 'N'
        else:
          s.send[SOUTH].en = s.recv.en
          s.out_dir = 'S'

      else:
        raise AssertionError( "Invalid input for dimension: %s " % dimension )

  def line_trace( s ):
    out_str = [ "" for _ in range( s.num_outports ) ]
    for i in range (s.num_outports):
      out_str[i] = "<{}>".format( s.send[i].en ) 
    return "pos:({},{}); src:({},{}); dst:({},{}); out_dir:({});\
 ({}|{}|{}|{}|{})".format( s.pos_x, s.pos_y, s.pkt.src_x, s.pkt.src_y, 
s.pkt.dst_x, s.pkt.dst_y, s.out_dir, out_str[0], out_str[1], out_str[2], 
out_str[3], out_str[4] )
