#=========================================================================
# DORYRouteUnitRTL.py
#=========================================================================
# A route unit with DOR-Y routing.
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 3, 2019

from pymtl import *
#from pclib.ifcs.EnRdyIfc import InEnRdyIfc, OutEnRdyIfc
from pclib.ifcs.SendRecvIfc import *

class DORYRouteUnitRTL( RTLComponent ):
  def construct( s, PacketType, PositionType, num_outports=5 ):

    # Constants 
    s.num_outports = num_outports
    NORTH = 0
    SOUTH = 1
    WEST  = 2
    EAST  = 3
    SELF  = 4

    # Interface
#    s.recv  = InEnRdyIfc( PacketType )
    s.recv  = RecvIfcRTL( PacketType )
    s.send  = [ SendIfcRTL (PacketType) for _ in range ( s.num_outports ) ]
    s.pos   = InVPort( PositionType )

    # Componets
    s.out_rdys = Wire( mk_bits( s.num_outports ) )
    s.out_dir  = OutVPort( Bits3  ) 

    # Connections
    for i in range( s.num_outports ):
      s.connect( s.recv.msg,    s.send[i].msg )
      s.connect( s.out_rdys[i], s.send[i].rdy )
    
    # Routing logic
    @s.update
    def up_ru_recv_rdy():
      s.out_dir = 0
      if s.pos.pos_x == s.recv.msg.dst_x and s.pos.pos_y == s.recv.msg.dst_y:
        s.out_dir = SELF
      elif s.recv.msg.dst_y < s.pos.pos_y:
        s.out_dir = NORTH
      elif s.recv.msg.dst_y > s.pos.pos_y:
        s.out_dir = SOUTH
      elif s.recv.msg.dst_x < s.pos.pos_x:
        s.out_dir = WEST
      else:
        s.out_dir = EAST
      s.recv.rdy =  s.send[s.out_dir].rdy

    @s.update
    def up_ru_send_en():
      for i in range( s.num_outports ):
        s.send[i].en = 0
      s.send[s.out_dir].en = s.recv.en and s.send[s.out_dir].rdy 

  def line_trace( s ):
    out_str = [ "" for _ in range( s.num_outports ) ]
    for i in range (s.num_outports):
      out_str[i] = "<{}>".format( s.send[i].en ) 

    return "({},{})->({},{}); dir:({}); ({}|{}|{}|{}|{}); recv.rdy({}); send.rdy({})".format(s.recv.msg.src_x, s.recv.msg.src_y, s.recv.msg.dst_x, s.recv.msg.dst_y, s.out_dir, out_str[0], out_str[1], out_str[2], out_str[3], out_str[4], s.recv.rdy, s.send[s.out_dir].rdy )
