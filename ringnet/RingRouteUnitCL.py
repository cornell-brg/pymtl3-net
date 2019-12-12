#=========================================================================
# RingRouteUnitCL.py
#=========================================================================
# Cycle level implementation of the route unit for ring network.
# It uses greedy routing algorithm.
#
# Author : Yanghui Ou
#   Date : May 16, 2019

from directions import *
from pymtl3 import *
from pymtl3.stdlib.cl.queues import BypassQueueCL


class RingRouteUnitCL( Component ):

  def construct( s, PacketType, PositionType, num_routers=4 ):

    # Constants

    s.num_outports = 3 # left, right, self
    s.total_dist = num_routers-1

    # Interface

    s.get  = NonBlockingCallerIfc()
    s.give = [ NonBlockingCalleeIfc() for _ in range ( s.num_outports ) ]
    s.pos  = InPort( PositionType )

    # Components

    s.rdy_lst = [ False for _ in range( s.num_outports ) ]
    s.msg     = None

    @s.update
    def ru_up_route():
      if s.msg is None and s.get.rdy():
        s.msg = s.get()

      s.rdy_lst = [ False for _ in range( s.num_outports ) ]
      if s.msg is not None:
        if s.msg.dst == s.pos:
          s.rdy_lst[SELF] = True
        else:
          if s.msg.dst > s.pos:
            right_dist = s.msg.dst - s.pos
            left_dist  = s.total_dist - right_dist
          else:
            left_dist  = s.msg.dst - s.pos
            right_dist = s.total_dist - left_dist
          if left_dist < right_dist:
            s.rdy_lst[LEFT] = True
          else:
            s.rdy_lst[RIGHT] = True

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
        M( s.get ) < U( ru_up_route ) < M( s.give[i] ),
      )

  def give_method( s ):
    assert s.msg is not None
    ret = s.msg
    s.msg = None
    return ret

  # TODO: CL line trace

  def line_trace( s ):
    return "{!s:12}".format( s.msg )
