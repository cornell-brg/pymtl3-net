"""
==========================================================================
DTRBfRouteUnitRTL.py
==========================================================================
RTL implementation of a route unit for butterfly network. It uses
destination tag routing.

Author : Yanghui Ou, Cheng Tan
  Date : April 6, 2019
"""
from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import SendIfcRTL, RecvIfcRTL


class DTRBflyRouteUnitRTL( Component ):

  def construct( s, PacketType, PositionType, num_outports, n_fly = 3 ):

    # Constants

    s.num_outports = num_outports
    k_ary    = num_outports
    OutType  = mk_bits( clog2( s.num_outports ) )
    rows     = k_ary ** ( n_fly - 1 )
    DstType  = mk_bits( clog2(k_ary) * n_fly )
    RowWidth = clog2( k_ary )
    END      = n_fly * RowWidth
    BEGIN    = END - RowWidth

    # Interface

    s.recv = RecvIfcRTL( PacketType )
    s.send = [ SendIfcRTL(PacketType ) for _ in range ( s.num_outports ) ]
    s.pos  = InPort( PositionType )

    # Componets

    s.out_dir  = Wire( OutType )
    s.send_val = [ Wire() for _ in range( s.num_outports ) ]
    s.send_rdy = Wire( mk_bits( s.num_outports ) )

    # Connections

    for i in range( s.num_outports ):
      s.send_rdy[i] //= s.send[i].rdy
      s.send_val[i] //= s.send[i].val

    # Routing logic

    @update
    def up_ru_routing():
      for i in range( s.num_outports ):
        s.send_val[i] @= 0

      if s.recv.val:
        s.out_dir @= s.recv.msg.dst[BEGIN : END]
        s.send_val[ s.out_dir ] @= 1

    @update
    def up_ru_send():
      s.recv.rdy @= s.send_rdy > 0

      for i in range( s.num_outports ):
        s.send[i].msg @= s.recv.msg

      if s.recv.val:
        s.send[ s.out_dir ].msg.dst @= s.recv.msg.dst << RowWidth

  # Line trace

  def line_trace( s ):
    out_str = [ "" for _ in range( s.num_outports ) ]
    for i in range (s.num_outports):
      out_str[i] = "{}".format( s.send[i] )

    return "{}({}){}".format( s.recv, s.out_dir, "|".join( out_str ) )
