"""
=========================================================================
DORXRouteUnitRTL.py
=========================================================================
A DOR route unit with get/give interface.

Author : Yanghui Ou, Cheng Tan
  Date : Mar 25, 2019
"""
from pymtl3 import *
from pymtl3.stdlib.ifcs import GetIfcRTL, GiveIfcRTL

from .directions import *


class DORXMeshRouteUnitRTL( Component ):

  def construct( s, PacketType, PositionType, num_outports ):

    # Interface

    s.get  = GetIfcRTL( PacketType )
    s.give = [ GiveIfcRTL(PacketType) for _ in range (num_outports) ]
    s.pos  = InPort( PositionType )

    # Componets

    s.out_dir  = Wire( mk_bits( clog2(num_outports) ) )
    s.give_ens = Wire( mk_bits( num_outports ) )

    # Connections

    for i in range( num_outports ):
      s.get.ret     //= s.give[i].ret
      s.give_ens[i] //= s.give[i].en

    # Routing logic
    @update
    def up_ru_routing():

      s.out_dir = Bits3(0)
      for i in range( num_outports ):
        s.give[i].rdy = Bits1(0)

      if s.get.rdy:
        if s.pos.pos_x == s.get.ret.dst_x and s.pos.pos_y == s.get.ret.dst_y:
          s.out_dir = SELF
        elif s.get.ret.dst_x < s.pos.pos_x:
          s.out_dir = WEST
        elif s.get.ret.dst_x > s.pos.pos_x:
          s.out_dir = EAST
        elif s.get.ret.dst_y > s.pos.pos_y:
          s.out_dir = NORTH
        else:
          s.out_dir = SOUTH
        s.give[ s.out_dir ].rdy = Bits1(1)

    @update
    def up_ru_give_en():
      s.get.en = s.give_ens > Bits5(0)

  # Line trace
  def line_trace( s ):
    out_str = "|".join([ str(x) for x in s.give ])
    return f"{s.get}({s.out_dir}){out_str}"
