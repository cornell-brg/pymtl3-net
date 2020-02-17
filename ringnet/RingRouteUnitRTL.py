"""
==========================================================================
RingRouteUnitRTL.py
==========================================================================
A ring route unit with get/give interface.

Author : Yanghui Ou, Cheng Tan
  Date : April 6, 2019
"""
from copy import deepcopy

from pymtl3 import *
from pymtl3.stdlib.ifcs import GetIfcRTL, GiveIfcRTL, SendIfcRTL

from .directions import *


class RingRouteUnitRTL( Component ):

  def construct( s, PacketType, PositionType, num_routers=4 ):

    # Constants
    s.num_outports = 3
    s.num_routers  = num_routers

    id_type    = mk_bits( clog2( num_routers ) )
    dist_type  = mk_bits( clog2( num_routers+1 ) )
    out_type   = mk_bits( s.num_outports )
    dir_type   = mk_bits( clog2( s.num_outports ) )
    s.last_idx = dist_type( num_routers-1 )

    # Interface

    s.get  = GetIfcRTL( PacketType )
    s.give = [ GiveIfcRTL (PacketType) for _ in range ( s.num_outports ) ]
    s.pos  = InPort( PositionType )

    # Componets

    s.out_dir  = Wire( mk_bits( clog2( s.num_outports ) ) )
    s.give_ens = Wire( mk_bits( s.num_outports ) )

    s.left_dist  = Wire( mk_bits( clog2(s.num_routers+1) ) )
    s.right_dist = Wire( mk_bits( clog2(s.num_routers+1) ) )
    s.give_msg_wire = Wire( PacketType )

    # Connections

    for i in range( s.num_outports ):
      s.give_ens[i] //= s.give[i].en

    # Routing logic
    @s.update
    def up_left_right_dist():
      if s.get.ret.dst < s.pos:
        s.left_dist  = dist_type(s.pos) - dist_type(s.get.ret.dst)
        s.right_dist = s.last_idx - dist_type(s.pos) + dist_type(s.get.ret.dst) + dist_type(1)
      else:
        s.left_dist  = dist_type(1) + s.last_idx + dist_type(s.pos) - dist_type(s.get.ret.dst)
        s.right_dist = dist_type(s.get.ret.dst) - dist_type(s.pos)

    @s.update
    def up_ru_routing():

      s.out_dir = dir_type(0)
      s.give_msg_wire = deepcopy( s.get.ret )
      for i in range( s.num_outports ):
        s.give[i].rdy = b1(0)

      if s.get.rdy:
        if s.pos == s.get.ret.dst:
          s.out_dir = dir_type(SELF)
        elif s.left_dist < s.right_dist:
          s.out_dir = dir_type(LEFT)
        else:
          s.out_dir = dir_type(RIGHT)

        if dist_type(s.pos) == s.last_idx and s.out_dir == dir_type(RIGHT):
          s.give_msg_wire.vc_id = b1(1)
        elif s.pos == id_type(0) and s.out_dir == dir_type(LEFT):
          s.give_msg_wire.vc_id = b1(1)

        s.give[ s.out_dir ].rdy = b1(1)
        s.give[ s.out_dir ].ret = s.give_msg_wire

    @s.update
    def up_ru_get_en():
      s.get.en = s.give_ens > out_type(0)

  # Line trace
  def line_trace( s ):

    out_str = [ "" for _ in range( s.num_outports ) ]
    for i in range (s.num_outports):
      out_str[i] = "{}".format( s.give[i] )

    return "{}({}){}".format( s.get, s.out_dir, "|".join( out_str ) )
