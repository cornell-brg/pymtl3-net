"""
=========================================================================
DORYMeshRouteUnitRTL.py
=========================================================================
A DOR route unit with get/give interface.

Author : Yanghui Ou, Cheng Tan
  Date : Mar 25, 2019
"""
from pymtl3             import *
from .directions        import *
from pymtl3.stdlib.ifcs import GetIfcRTL, GiveIfcRTL

class DORYMeshRouteUnitRTL( Component ):

  def construct( s, MsgType, PositionType, num_outports = 5 ):

    # Interface

    s.get  = GetIfcRTL( MsgType )
    s.give = [ GiveIfcRTL (MsgType) for _ in range ( num_outports ) ]
    s.pos  = InPort( PositionType )

    # Componets

    s.give_ens = Wire( mk_bits( num_outports ) )

    # Connections

    for i in range( num_outports ):
      s.get.msg     //= s.give[i].msg
      s.give_ens[i] //= s.give[i].en

    # Routing logic
    @s.update
    def up_ru_routing():
      s.give[0].rdy = b1(0)
      s.give[1].rdy = b1(0)
      s.give[2].rdy = b1(0)
      s.give[3].rdy = b1(0)
      s.give[4].rdy = b1(0)

      if s.get.rdy:
        if s.pos.pos_x == s.get.msg.dst_x and s.pos.pos_y == s.get.msg.dst_y:
          s.give[4].rdy = b1(1)
        elif s.get.msg.dst_y < s.pos.pos_y:
          s.give[1].rdy = b1(1)
        elif s.get.msg.dst_y > s.pos.pos_y:
          s.give[0].rdy = b1(1)
        elif s.get.msg.dst_x < s.pos.pos_x:
          s.give[2].rdy = b1(1)
        else:
          s.give[3].rdy = b1(1)

    @s.update
    def up_ru_get_en():
      s.get.en = s.give_ens > b5(0)

  # Line trace
  def line_trace( s ):

    out_str = "|".join([ str(x) for x in s.give ])
    return f"{s.get}(){out_str}"
