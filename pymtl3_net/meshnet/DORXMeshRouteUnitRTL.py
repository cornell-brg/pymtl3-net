"""
=========================================================================
DORXRouteUnitRTL.py
=========================================================================
A DOR route unit with get/give interface.

Author : Yanghui Ou, Cheng Tan
  Date : Mar 25, 2019
"""
from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import RecvIfcRTL, SendIfcRTL

from .directions import *


class DORXMeshRouteUnitRTL( Component ):

  def construct( s, PacketType, PositionType, num_outports ):

    # Interface

    s.recv = RecvIfcRTL( PacketType )
    s.send = [ SendIfcRTL(PacketType) for _ in range (num_outports) ]
    s.pos  = InPort( PositionType )

    # Componets

    s.out_dir  = Wire( mk_bits( clog2(num_outports) ) )
    s.send_rdy = Wire( mk_bits( num_outports ) )

    # Connections

    for i in range( num_outports ):
      s.recv.msg    //= s.send[i].msg
      s.send_rdy[i] //= s.send[i].rdy

    # Routing logic
    @update
    def up_ru_routing():

      s.out_dir @= Bits3(0)
      for i in range( num_outports ):
        s.send[i].val @= Bits1(0)

      if s.recv.val:
        if s.pos.pos_x == s.recv.msg.dst_x and s.pos.pos_y == s.recv.msg.dst_y:
          s.out_dir @= SELF
        elif s.recv.msg.dst_x < s.pos.pos_x:
          s.out_dir @= WEST
        elif s.recv.msg.dst_x > s.pos.pos_x:
          s.out_dir @= EAST
        elif s.recv.msg.dst_y > s.pos.pos_y:
          s.out_dir @= NORTH
        else:
          s.out_dir @= SOUTH
        s.send[ s.out_dir ].val @= Bits1(1)

    @update
    def up_ru_recv_rdy():
      s.recv.rdy @= s.send_rdy[ s.out_dir ]

  # Line trace
  def line_trace( s ):
    out_str = "|".join([ str(x) for x in s.send ])
    return f"{s.recv}({s.out_dir}){out_str}"
