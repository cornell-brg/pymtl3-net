"""
=========================================================================
DORXRouteUnitRTL.py
=========================================================================
A DOR-X route unit with val/rdy interface for CMesh.

Author : Yanghui Ou, Cheng Tan
  Date : Mar 25, 2019
"""
from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import RecvIfcRTL, SendIfcRTL

from .directions import *


class DORXCMeshRouteUnitRTL( Component ):

  def construct( s, PacketType, PositionType, num_outports = 8 ):

    # Constants

    s.num_outports = num_outports
    TType = mk_bits( clog2(num_outports) )

    # Interface

    s.recv = RecvIfcRTL( PacketType )
    s.send = [ SendIfcRTL (PacketType) for _ in range ( s.num_outports ) ]
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

      s.out_dir @= 0
      for i in range( s.num_outports ):
        s.send[i].val @= Bits1(0)

      if s.recv.val:
        if (s.pos.pos_x == s.recv.msg.dst_x) & (s.pos.pos_y == s.recv.msg.dst_y):
          s.out_dir @= SELF + zext( s.recv.msg.dst_ter, TType )
        elif s.recv.msg.dst_x < s.pos.pos_x:
          s.out_dir @= WEST
        elif s.recv.msg.dst_x > s.pos.pos_x:
          s.out_dir @= EAST
        elif s.recv.msg.dst_y < s.pos.pos_y:
          s.out_dir @= SOUTH
        else:
          s.out_dir @= NORTH
        s.send[ s.out_dir ].val @= Bits1(1)

    @update
    def up_ru_recv_rdy():
      s.recv.rdy @= s.send_rdy[ s.out_dir ]

  # Line trace

  def line_trace( s ):
    out_str = "".join([ f"{s.send[i]}" for i in range( s.num_outports ) ])
    return f"{s.recv}(){out_str}"
