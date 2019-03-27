#=========================================================================
# DORXRouteUnitGetGiveRTL.py
#=========================================================================
# A DOR route unit with get/give interface.
#
# Author : Yanghui Ou, Cheng Tan
#   Date : Mar 25, 2019

from pymtl import *
from ocn_pclib.ifcs import GetIfcRTL, GiveIfcRTL

class DORXRouteUnitGetGiveRTL( ComponentLevel6 ):

  def construct( s, PacketType, PositionType ):

    # Constants 

    s.num_outports = 5
    # TODO: define thses constants else where?
    NORTH = 0
    SOUTH = 1
    WEST  = 2
    EAST  = 3
    SELF  = 4

    # Interface

    s.get  = GetIfcRTL( PacketType )
    s.give  = [ GiveIfcRTL (PacketType) for _ in range ( s.num_outports ) ]
    s.pos   = InVPort( PositionType )

    # Componets

    s.out_dir  = Wire( mk_bits( clog2( s.num_outports ) ) )
    s.give_ens = Wire( mk_bits( s.num_outports ) ) 

    # Connections

    for i in range( s.num_outports ):
      s.connect( s.get.msg,    s.give[i].msg )
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
        elif s.get.msg.dst_x < s.pos.pos_x:
          s.out_dir = WEST
        elif s.get.msg.dst_x > s.pos.pos_x:
          s.out_dir = EAST
        elif s.get.msg.dst_y < s.pos.pos_y:
          s.out_dir = NORTH
        else:
          s.out_dir = SOUTH
        s.give[ s.out_dir ].rdy = 1

    @s.update
    def up_ru_give_en():
      s.get.en = s.give_ens > 0 

  # Line trace
  def line_trace( s ):

    out_str = [ "" for _ in range( s.num_outports ) ]
    for i in range (s.num_outports):
      out_str[i] = "{}".format( s.give[i] ) 

    return "{}({}){}".format( s.get, s.out_dir, "|".join( out_str ) )
