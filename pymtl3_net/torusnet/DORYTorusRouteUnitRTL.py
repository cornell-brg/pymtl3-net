"""
==========================================================================
DORYTorusRouteUnitRTL.py
==========================================================================
A DOR route unit with get/give interface for Torus topology.

Author : Yanghui Ou, Cheng Tan
  Date : June 29, 2019
"""
from copy import deepcopy

from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import RecvIfcRTL, SendIfcRTL

from .directions import *


class DORYTorusRouteUnitRTL( Component ):

  def construct( s, PacketType, PositionType, ncols=2, nrows=2 ):

    # Constants

    num_outports = 5
    s.ncols = ncols
    s.nrows = nrows

    # Here we add 1 to avoid overflow

    posx_type     = mk_bits( clog2( ncols ) )
    posy_type     = mk_bits( clog2( nrows ) )
    ns_dist_type  = mk_bits( clog2( nrows+1 ) )
    we_dist_type  = mk_bits( clog2( ncols+1 ) )

    s.last_row_id = nrows-1
    s.last_col_id = ncols-1

    # Interface

    s.recv = RecvIfcRTL( PacketType )
    s.send = [ SendIfcRTL (PacketType) for _ in range ( num_outports ) ]
    s.pos  = InPort( PositionType )

    # Componets

    s.out_dir       = Wire( Bits3        )
    s.send_rdy      = Wire( Bits5        )
    s.turning       = Wire( Bits1        )
    s.north_dist    = Wire( ns_dist_type )
    s.south_dist    = Wire( ns_dist_type )
    s.west_dist     = Wire( we_dist_type )
    s.east_dist     = Wire( we_dist_type )
    s.send_msg_wire = Wire( PacketType   )

    # Connections

    for i in range( num_outports ):
      s.send_rdy[i]   //= s.send[i].rdy
      s.send_msg_wire //= s.send[i].msg

    # Calculate distance

    @update
    def up_ns_dist():
      if s.recv.msg.dst_y < s.pos.pos_y:
        s.south_dist @= zext(s.pos.pos_y, ns_dist_type) - zext(s.recv.msg.dst_y, ns_dist_type)
        s.north_dist @= s.last_row_id - zext(s.pos.pos_y, ns_dist_type) + 1 + zext(s.recv.msg.dst_y, ns_dist_type)
      else:
        s.south_dist @= zext(s.pos.pos_y, ns_dist_type) + 1 + s.last_row_id - zext(s.recv.msg.dst_y, ns_dist_type)
        s.north_dist @= zext(s.recv.msg.dst_y, ns_dist_type) - zext(s.pos.pos_y, ns_dist_type)

    @update
    def up_we_dist():
      if s.recv.msg.dst_x < s.pos.pos_x:
        s.west_dist @= zext(s.pos.pos_x, we_dist_type) - zext(s.recv.msg.dst_x,we_dist_type)
        s.east_dist @= s.last_col_id - zext(s.pos.pos_x, we_dist_type) + 1 + zext(s.recv.msg.dst_x, we_dist_type)
      else:
        s.west_dist @= zext(s.pos.pos_x, we_dist_type) + 1 + s.last_col_id - zext(s.recv.msg.dst_x, we_dist_type)
        s.east_dist @= zext(s.recv.msg.dst_x, we_dist_type) - zext(s.pos.pos_x, we_dist_type)

    # Routing logic

    @update
    def up_ru_routing():

      s.send_msg_wire @= s.recv.msg
      s.out_dir @= 0
      s.turning @= 0

      for i in range( num_outports ):
        s.send[i].val @= 0

      if s.recv.val:
        if (s.pos.pos_x == s.recv.msg.dst_x) & (s.pos.pos_y == s.recv.msg.dst_y):
          s.out_dir @= SELF
        elif s.recv.msg.dst_y != s.pos.pos_y:
          s.out_dir @= NORTH if s.north_dist < s.south_dist else SOUTH
        else:
          s.out_dir @= WEST if s.west_dist < s.east_dist else EAST

        # Turning logic

        s.turning @= ( s.recv.msg.src_x == s.pos.pos_x ) & \
                     ( s.recv.msg.src_y != s.pos.pos_y ) & \
                     ( s.out_dir == WEST ) | ( s.out_dir == EAST )

        # Dateline logic

        if s.turning:
          s.send_msg_wire.vc_id @= 0

        if (s.pos.pos_x == 0) & (s.out_dir == WEST):
          s.send_msg_wire.vc_id @= 1
        elif (s.pos.pos_x == s.last_col_id) & (s.out_dir == EAST):
          s.send_msg_wire.vc_id @= 1
        elif (s.pos.pos_y == 0) & (s.out_dir == SOUTH):
          s.send_msg_wire.vc_id @= 1
        elif (s.pos.pos_y == s.last_row_id) & (s.out_dir == NORTH):
          s.send_msg_wire.vc_id @= 1

        s.send[ s.out_dir ].val @= 1

    @update
    def up_ru_recv_rdy():
      s.recv.rdy @= s.send[ s.out_dir ].rdy

  # Line trace

  def line_trace( s ):
    out_str = "|".join([ str(x) for x in s.send ])
    dir_str = (
      "N" if s.out_dir == NORTH else
      "S" if s.out_dir == SOUTH else
      "W" if s.out_dir == WEST  else
      "E"
    )
    turn_str = "t" if s.turning else " "
    return f"{s.recv}({dir_str},{turn_str}){out_str}"
