#=========================================================================
# RingRouteUnitRTL.py
#=========================================================================
# A ring route unit with get/give interface.
#
# Author : Yanghui Ou, Cheng Tan
#   Date : April 6, 2019

from copy import deepcopy
from pymtl3          import *
from directions      import *
from pymtl3.stdlib.ifcs import GetIfcRTL, SendIfcRTL, GiveIfcRTL

class RingRouteUnitRTL( Component ):

  def construct( s, PacketType, PositionType, num_outports, num_routers=4 ):

    # Constants
    s.num_outports = num_outports
    s.num_routers  = num_routers

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

      s.out_dir = 0
      s.give_msg_wire = deepcopy( s.get.msg )
      for i in range( s.num_outports ):
        s.give[i].rdy = 0

      if s.get.rdy:
        if s.pos == s.get.msg.dst:
          s.out_dir = SELF
        elif s.get.msg.dst < s.pos and \
             s.pos - s.get.msg.dst <= num_routers/2:
          s.out_dir = LEFT
        elif s.get.msg.dst > s.pos and \
             s.get.msg.dst - s.pos > num_routers/2:
          s.out_dir = LEFT
        else:
          s.out_dir = RIGHT

        if s.pos == s.num_routers-1 and s.out_dir == RIGHT:
          s.give_msg_wire.vc_id = 1
        elif s.pos == 0 and s.out_dir == LEFT:
          s.give_msg_wire.vc_id = 1

        s.give[ s.out_dir ].rdy = 1
        s.give[ s.out_dir ].msg = s.give_msg_wire

    @s.update
    def up_ru_get_en():
      s.get.en = s.give_ens > 0

  # Line trace
  def line_trace( s ):

    out_str = [ "" for _ in range( s.num_outports ) ]
    for i in range (s.num_outports):
      out_str[i] = "{}".format( s.give[i] )

    return "{}({}){}".format( s.get, s.out_dir, "|".join( out_str ) )
