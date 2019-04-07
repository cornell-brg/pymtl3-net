#=========================================================================
# DORYTorusRouteUnitGetGiveRTL.py
#=========================================================================
# A DOR route unit with get/give interface for Torus topology.
#
# Author : Cheng Tan
#   Date : Mar 29, 2019

from pymtl import *
from ocn_pclib.ifcs import GetIfcRTL, GiveIfcRTL

from Configs        import configure_network

class DORYTorusRouteUnitRTL( Component ):

  def construct( s, PacketType, PositionType, cols=2, rows=2 ):

    # Constants 
    configs = configure_network()
    s.num_outports = configs.router_outports
    s.cols = cols
    s.rows = rows

    # TODO: define thses constants else where?
    NORTH = 0
    SOUTH = 1
    WEST  = 2
    EAST  = 3
    SELF  = 4

    # Interface

    s.get  = GetIfcRTL( PacketType )
    s.give = [ GiveIfcRTL (PacketType) for _ in range ( s.num_outports ) ]
    s.pos  = InPort( PositionType )

    # Componets

    s.out_dir  = Wire( mk_bits( clog2( s.num_outports ) ) )
    s.give_ens = Wire( mk_bits( s.num_outports ) ) 

    # Connections

    for i in range( s.num_outports ):
#      s.connect( s.get.msg,     s.give[i].msg )
      s.connect( s.give_ens[i], s.give[i].en  )
    
    # Routing logic
    @s.update
    def up_ru_routing():
 
      s.out_dir = 0
      for i in range( s.num_outports ):
        s.give[i].rdy = 0

      if s.get.rdy:
        if s.pos.pos_x == s.get.msg.dst_x and s.pos.pos_y == s.get.msg.dst_y:
          s.out_dir = SELF
        elif s.get.msg.dst_y < s.pos.pos_y:
          if s.pos.pos_y - s.get.msg.dst_y <= s.rows - s.pos.pos_y + s.get.msg.dst_y:
            s.out_dir = NORTH
          else:
            s.out_dir = SOUTH
        elif s.get.msg.dst_y > s.pos.pos_y:
          if s.get.msg.dst_y - s.pos.pos_y <= s.rows - s.get.msg.dst_y + s.pos.pos_y:
            s.out_dir = SOUTH
          else:
            s.out_dir = NORTH
        elif s.get.msg.dst_x < s.pos.pos_x:
          if s.pos.pos_x - s.get.msg.dst_x <= s.cols - s.pos.pos_x + s.get.msg.dst_x:
            s.out_dir = WEST
          else:
            s.out_dir = EAST
        else:
          if s.get.msg.dst_x - s.pos.pos_x <= s.rows - s.get.msg.dst_x + s.pos.pos_x:
            s.out_dir = EAST
          else:
            s.out_dir = WEST
        s.give[ s.out_dir ].rdy = 1
        s.give[ s.out_dir ].msg = s.get.msg

    @s.update
    def up_ru_get_en():
      s.get.en = s.give_ens > 0 

  # Line trace
  def line_trace( s ):

    out_str = [ "" for _ in range( s.num_outports ) ]
    for i in range (s.num_outports):
      out_str[i] = "{}".format( s.give[i] ) 

    return "{}({}){}".format( s.get, s.out_dir, "|".join( out_str ) )
