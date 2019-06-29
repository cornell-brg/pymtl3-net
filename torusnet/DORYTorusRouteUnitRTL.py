#=========================================================================
# DORYTorusRouteUnitGetGiveRTL.py
#=========================================================================
# A DOR route unit with get/give interface for Torus topology.
#
# Author : Cheng Tan
#   Date : Mar 29, 2019

from pymtl3             import *
from directions         import *
from pymtl3.stdlib.ifcs import GetIfcRTL, GiveIfcRTL
from copy import deepcopy

class DORYTorusRouteUnitRTL( Component ):

  def construct( s, PacketType, PositionType, num_outports, cols=2, rows=2 ):

    # Constants 
    s.num_outports = num_outports
    s.cols = cols
    s.rows = rows

    # Interface

    s.get  = GetIfcRTL( PacketType )
    s.give = [ GiveIfcRTL (PacketType) for _ in range ( s.num_outports ) ]
    s.pos  = InPort( PositionType )

    # Componets

    s.out_dir  = Wire( mk_bits( clog2( s.num_outports ) ) )
    s.give_ens = Wire( mk_bits( s.num_outports ) ) 

    s.give_msg_wire = Wire( PacketType )

    # Connections

    for i in range( s.num_outports ):
#      s.connect( s.get.msg,     s.give[i].msg )
      s.connect( s.give_ens[i], s.give[i].en  )
    
    # Routing logic
    @s.update
    def up_ru_routing():
 
      s.give_msg_wire = deepcopy( s.get.msg )
      s.out_dir = 0
      for i in range( s.num_outports ):
        s.give[i].rdy = 0

      if s.get.rdy:
        if s.pos.pos_x == s.get.msg.dst_x and s.pos.pos_y == s.get.msg.dst_y:
          s.out_dir = SELF
        elif s.get.msg.dst_y < s.pos.pos_y:
          if s.pos.pos_y - s.get.msg.dst_y <= s.rows - s.pos.pos_y + s.get.msg.dst_y:
            s.out_dir = SOUTH
          else:
            s.out_dir = NORTH
            print "what: ", s.get.msg
        elif s.get.msg.dst_y > s.pos.pos_y:
          if s.get.msg.dst_y - s.pos.pos_y <= s.rows - s.get.msg.dst_y + s.pos.pos_y:
            s.out_dir = NORTH
            print "what: ", s.get.msg
          else:
            s.out_dir = SOUTH
        elif s.get.msg.dst_x < s.pos.pos_x:
          if s.pos.pos_x - s.get.msg.dst_x <= s.cols - s.pos.pos_x + s.get.msg.dst_x:
            s.out_dir = WEST
          else:
            s.out_dir = EAST
        else:
          if s.get.msg.dst_x - s.pos.pos_x <= s.cols - s.get.msg.dst_x + s.pos.pos_x:
            s.out_dir = EAST
          else:
            s.out_dir = WEST

        if s.pos.pos_x == 0 and s.out_dir == WEST:
          s.give_msg_wire.vc_id = 1
        elif s.pos.pos_x == cols - 1 and s.out_dir == EAST:
          s.give_msg_wire.vc_id = 1
        elif s.pos.pos_y == 0 and s.out_dir == SOUTH:
          s.give_msg_wire.vc_id = 1
        elif s.pos.pos_y == rows - 1 and s.out_dir == NORTH:
          s.give_msg_wire.vc_id = 1

        s.give[ s.out_dir ].rdy = 1
        s.give[ s.out_dir ].msg = s.give_msg_wire
#        print 'get is rdy??????   pos: ', s.pos, '; msg: ', s.give_msg_wire,\
#                '; s.out_dir: ', s.out_dir, '; s.get_msg: ', s.get.msg, '; rdy: ',\
#                s.get.rdy, '; get.en: ', s.get.en
#      else:
#        print 'get is not rdy!!!!!&&&&&&&& pos: ', s.pos, '; enabled?:', s.get.en

    @s.update
    def up_ru_get_en():
#      print 'see get enable??: ', s.get.en, '; pos: ', s.pos
      s.get.en = s.give_ens > 0 

#    s.add_constraints( U( up_ru_get_en ) < U ( up_ru_routing ) )

  # Line trace
  def line_trace( s ):

    out_str = [ "" for _ in range( s.num_outports ) ]
    for i in range (s.num_outports):
      out_str[i] = "{}".format( s.give[i] ) 

    return "{}({}){}*{}*".format( s.get, s.out_dir, "|".join( out_str ), s.give_msg_wire )
