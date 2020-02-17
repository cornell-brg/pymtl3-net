#=========================================================================
# DORYMeshRouteUnitCL.py
#=========================================================================
# Cycle level implementation of a Y-DOR route unit.
#
# Author : Yanghui Ou
#   Date : May 21, 2019

from directions import *
from pymtl3 import *
from pymtl3.stdlib.cl.queues import BypassQueueCL


class DORYMeshRouteUnitCL( Component ):

  def construct( s, PacketType, PositionType ):

    # Local parameters

    s.num_outports = 5

    # Interface

    s.get  = CallerIfcCL( Type=PacketType )
    s.give = [ CalleeIfcCL( Type=PacketType ) for _ in range( s.num_outports ) ]
    s.pos  = InPort( PositionType )

    # Components

    s.rdy_lst = [ False for _ in range( s.num_outports ) ]
    s.pkt     = None

    @s.update
    def ru_up_route():
      if s.pkt is None and s.get.rdy():
        s.pkt = s.get()
      s.rdy_lst = [ False for _ in range( s.num_outports ) ]
      if s.pkt is not None:
        if s.pkt.dst_x == s.pos.pos_x and s.pkt.dst_y == s.pos.pos_y:
          s.rdy_lst[SELF] = True
        elif s.pkt.dst_y > s.pos.pos_y:
          s.rdy_lst[NORTH] = True
        elif s.pkt.dst_y < s.pos.pos_y:
          s.rdy_lst[SOUTH] = True
        elif s.pkt.dst_x < s.pos.pos_x:
          s.rdy_lst[WEST] = True
        else:
          s.rdy_lst[EAST] = True

    # Assign method and ready

    for i in range( s.num_outports ):
      def gen_give_rdy( s, port_id ):
        def give_rdy():
          if s.pkt is not None:
            return s.rdy_lst[port_id]
          else:
            return False
        return give_rdy

      s.give[i].rdy.method = gen_give_rdy( s, i )
      s.give[i].method.method = s.give_method

    for i in range( s.num_outports ):
      s.add_constraints(
        M( s.get ) < U( ru_up_route ) < M( s.give[i] ),
      )


  def give_method( s ):
    assert s.pkt is not None
    ret = s.pkt
    s.pkt = None
    return ret

  def line_trace( s ):
    out_trace = "|".join([ str(s.give[i]) for i in range(s.num_outports) ])
    return f"{s.get}(){out_trace}"
