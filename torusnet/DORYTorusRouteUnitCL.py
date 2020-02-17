#=========================================================================
# DORYTorusRouteUnitCL.py
#=========================================================================
# A DOR route unit with get/give interface for Torus topology in CL.
#
# Author : Cheng Tan
#   Date : May 20, 2019

from directions import *
from pymtl3 import *


class DORYTorusRouteUnitCL( Component ):

  def construct( s,
                 PacketType,
                 PositionType,
                 num_outports,
                 cols=2,
                 rows=2 ):

    # Constants
    s.num_outports = num_outports
    s.cols = cols
    s.rows = rows

    # Interface

    s.get  = CallerIfcCL()
    s.give = [ CalleeIfcCL() for _ in range ( s.num_outports ) ]
    s.pos  = InPort( PositionType )

    # Componets

    s.rdy_lst = [ False for _ in range( s.num_outports ) ]
    s.msg     = None

    # Routing logic

    @s.update
    def up_ru_routing():

      if s.msg is None and s.get.rdy():
        s.msg = s.get()
      if s.msg is not None:
        if s.pos.pos_x == s.msg.dst_x and s.pos.pos_y == s.msg.dst_y:
          s.rdy_lst[SELF] = True
        elif s.msg.dst_y < s.pos.pos_y:
          if s.pos.pos_y - s.msg.dst_y <= s.rows - s.pos.pos_y + s.msg.dst_y:
            s.rdy_lst[SOUTH] = True
          else:
            s.rdy_lst[NORTH] = True
        elif s.msg.dst_y > s.pos.pos_y:
          if s.msg.dst_y - s.pos.pos_y <= s.rows - s.msg.dst_y + s.pos.pos_y:
            s.rdy_lst[NORTH] = True
          else:
            s.rdy_lst[SOUTH] = True
        elif s.msg.dst_x < s.pos.pos_x:
          if s.pos.pos_x - s.msg.dst_x <= s.cols - s.pos.pos_x + s.msg.dst_x:
            s.rdy_lst[WEST] = True
          else:
            s.rdy_lst[EAST] = True
        else:
          if s.msg.dst_x - s.pos.pos_x <= s.rows - s.msg.dst_x + s.pos.pos_x:
            s.rdy_lst[EAST] = True
          else:
            s.rdy_lst[WEST] = True
      else:
        s.rdy_lst = [ False for _ in range( s.num_outports ) ]

    # Assign method and ready

    for i in range( s.num_outports ):
      def gen_give_rdy( s, port_id ):
        def give_rdy():
          if s.msg is not None:
            return s.rdy_lst[port_id]
          else:
            return False
        return give_rdy

      s.give[i].rdy.method = gen_give_rdy( s, i )
      s.give[i].method.method = s.give_method

    for i in range( s.num_outports ):
      s.add_constraints(
        M( s.get ) < U( up_ru_routing ) < M( s.give[i] ),
      )

  def give_method( s ):
    assert s.msg is not None
    ret = s.msg
    s.msg = None
    return ret

   # TODO: CL line trace

  def line_trace( s ):
    out_str = "|".join([ str(s.give[i]) for i in range( s.num_outports ) ])
    return f"{s.get}(){out_str}"
