"""
==========================================================================
RingRouteUnitRTL.py
==========================================================================
A ring route unit with val/rdy interface.

Author : Yanghui Ou, Cheng Tan
  Date : April 6, 2019
"""
from copy import deepcopy

from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import RecvIfcRTL, SendIfcRTL

from .directions import *


class RingRouteUnitRTL( Component ):

  def construct( s, PacketType, PositionType, num_routers=4 ):

    # Constants
    s.num_outports = 3
    s.num_routers  = num_routers

    DistType  = mk_bits( clog2( num_routers ) )
    s.last_idx = DistType( num_routers-1 )

    # Interface

    s.recv = RecvIfcRTL( PacketType )
    s.send = [ SendIfcRTL (PacketType) for _ in range ( s.num_outports ) ]
    s.pos  = InPort( PositionType )

    # Componets

    s.out_dir  = Wire( mk_bits( clog2( s.num_outports ) ) )
    s.send_rdy = Wire( mk_bits( s.num_outports ) )

    s.left_dist     = Wire( DistType )
    s.right_dist    = Wire( DistType )
    s.send_msg_wire = Wire( PacketType )

    # Connections

    for i in range( s.num_outports ):
      s.send_rdy[i] //= s.send[i].rdy

    # Routing logic
    @update
    def up_left_right_dist():
      if s.recv.msg.dst < s.pos:
        s.left_dist  @= zext(s.pos, DistType) - zext(s.recv.msg.dst, DistType)
        s.right_dist @= zext(s.last_idx, DistType) - zext(s.pos, DistType) + zext(s.recv.msg.dst, DistType) + 1
      else:
        s.left_dist  @= 1 + zext(s.last_idx, DistType) + zext(s.pos, DistType) - zext(s.recv.msg.dst, DistType)
        s.right_dist @= zext(s.recv.msg.dst, DistType) - zext(s.pos, DistType)

    @update
    def up_ru_routing():

      s.out_dir @= 0
      s.send_msg_wire @= s.recv.msg
      for i in range( s.num_outports ):
        s.send[i].val @= 0

      if s.recv.val:
        if s.pos == s.recv.msg.dst:
          s.out_dir @= SELF
        elif s.left_dist < s.right_dist:
          s.out_dir @= LEFT
        else:
          s.out_dir @= RIGHT

        if ( s.pos == s.last_idx ) & ( s.out_dir == RIGHT ):
          s.send_msg_wire.vc_id @= 1
        elif ( s.pos == 0 ) & ( s.out_dir == LEFT ):
          s.send_msg_wire.vc_id @= 1

        s.send[ s.out_dir ].val @= 1
        s.send[ s.out_dir ].msg @= s.send_msg_wire

    @update
    def up_ru_recv_rdy():
      s.recv.rdy @= s.send_rdy[ s.out_dir ]

  # Line trace
  def line_trace( s ):

    out_str = [ "" for _ in range( s.num_outports ) ]
    for i in range (s.num_outports):
      out_str[i] = f"{s.send[i]}"

    return "{}({}){}".format( s.recv, s.out_dir, "|".join( out_str ) )
