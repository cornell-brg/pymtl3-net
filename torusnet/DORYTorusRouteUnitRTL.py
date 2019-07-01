"""
==========================================================================
DORYTorusRouteUnitRTL.py
==========================================================================
A DOR route unit with get/give interface for Torus topology.

Author : Yanghui Ou, Cheng Tan
  Date : June 29, 2019
"""
from pymtl3             import *
from directions         import *
from pymtl3.stdlib.ifcs import GetIfcRTL, GiveIfcRTL
from copy import deepcopy

class DORYTorusRouteUnitRTL( Component ):

  def construct( s, PacketType, PositionType, ncols=2, nrows=2 ):

    # Constants
    s.num_outports = 5
    s.ncols = ncols
    s.nrows = nrows

    # Here we add 1 to avoid overflow
    posx_type     = mk_bits( clog2( ncols ) )
    posy_type     = mk_bits( clog2( nrows ) )
    ns_dist_type  = mk_bits( clog2( nrows+1 ) )
    we_dist_type  = mk_bits( clog2( ncols+1 ) )

    s.last_row_id = ns_dist_type( nrows-1 )
    s.last_col_id = we_dist_type( ncols-1 )

    # Interface
    s.get  = GetIfcRTL( PacketType )
    s.give = [ GiveIfcRTL (PacketType) for _ in range ( s.num_outports ) ]
    s.pos  = InPort( PositionType )

    # Componets
    s.out_dir       = Wire( Bits3        )
    s.give_ens      = Wire( Bits5        )
    s.turning       = Wire( Bits1        )
    s.north_dist    = Wire( ns_dist_type )
    s.south_dist    = Wire( ns_dist_type )
    s.west_dist     = Wire( we_dist_type )
    s.east_dist     = Wire( we_dist_type )
    s.give_msg_wire = Wire( PacketType   )

    # Connections
    for i in range( s.num_outports ):
      s.connect( s.give_ens[i],   s.give[i].en  )
      s.connect( s.give_msg_wire, s.give[i].msg )

    # Calculate distance
    @s.update
    def up_ns_dist():
      if s.get.msg.dst_y < s.pos.pos_y:
        s.south_dist = s.pos.pos_y - s.get.msg.dst_y
        s.north_dist = s.last_row_id - s.pos.pos_y + ns_dist_type(1) + s.get.msg.dst_y
      else:
        s.south_dist = s.pos.pos_y + ns_dist_type(1) + s.last_row_id - s.get.msg.dst_y
        s.north_dist = s.get.msg.dst_y - s.pos.pos_y

    @s.update
    def up_we_dist():
      if s.get.msg.dst_x < s.pos.pos_x:
        s.west_dist = s.pos.pos_x - s.get.msg.dst_x
        s.east_dist = s.last_col_id - s.pos.pos_x + ns_dist_type(1) + s.get.msg.dst_y
      else:
        s.west_dist = s.pos.pos_x + ns_dist_type(1) + s.last_col_id - s.get.msg.dst_y
        s.east_dist = s.get.msg.dst_y - s.pos.pos_x


    # Routing logic
    @s.update
    def up_ru_routing():

      s.give_msg_wire = deepcopy( s.get.msg )
      s.out_dir = b3(0)
      s.turning = b1(0)

      for i in range( s.num_outports ):
        s.give[i].rdy = b1(0)

      if s.get.rdy:
        if s.pos.pos_x == s.get.msg.dst_x and s.pos.pos_y == s.get.msg.dst_y:
          s.out_dir = SELF
        elif s.get.msg.dst_y != s.pos.pos_y:
          s.out_dir = NORTH if s.north_dist < s.south_dist else SOUTH
        else:
          s.out_dir = WEST if s.west_dist < s.east_dist else EAST

        # Turning logic
        s.turning = ( s.get.msg.src_x == s.pos.pos_x ) & ( s.get.msg.src_y != s.pos.pos_y ) & (s.out_dir == WEST | s.out_dir == EAST )

        # Dateline logic
        if s.turning:
          s.give_msg_wire.vc_id = b1(0)
        elif s.pos.pos_x == posx_type(0) and s.out_dir == WEST:
          s.give_msg_wire.vc_id = b1(1)
        elif s.pos.pos_x == s.last_col_id and s.out_dir == EAST:
          s.give_msg_wire.vc_id = b1(1)
        elif s.pos.pos_y == posy_type(0) and s.out_dir == SOUTH:
          s.give_msg_wire.vc_id = b1(1)
        elif s.pos.pos_y == s.last_col_id and s.out_dir == NORTH:
          s.give_msg_wire.vc_id = b1(1)

        s.give[ s.out_dir ].rdy = b1(1)
        # s.give[ s.out_dir ].msg = s.give_msg_wire

    @s.update
    def up_ru_get_en():
      s.get.en = s.give_ens > 0

  # Line trace
  def line_trace( s ):

    out_str = [ "" for _ in range( s.num_outports ) ]
    for i in range (s.num_outports):
      out_str[i] = "{}".format( s.give[i] )

    return "{}({},{}){}".format(
      s.get,
      "N" if s.out_dir == NORTH else
      "S" if s.out_dir == SOUTH else
      "W" if s.out_dir == WEST  else
      "E",
      "t" if s.turning else " ",
      "|".join( out_str ),
    )
