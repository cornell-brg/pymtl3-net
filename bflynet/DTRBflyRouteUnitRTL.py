"""
==========================================================================
DTRBfRouteUnitRTL.py
==========================================================================
RTL implementation of a route unit for butterfly network. It uses
destination tag routing.

Author : Yanghui Ou, Cheng Tan
  Date : April 6, 2019
"""
from copy import deepcopy

from pymtl3 import *
from pymtl3.stdlib.ifcs import GetIfcRTL, GiveIfcRTL


class DTRBflyRouteUnitRTL( Component ):

  def construct( s, PacketType, PositionType, num_outports, n_fly = 3 ):

    # Constants

    s.num_outports = num_outports
    k_ary    = num_outports
    OutType  = mk_bits( clog2( s.num_outports ) )
    rows     = k_ary ** ( n_fly - 1 )
    DstType = mk_bits( clog2(k_ary) * n_fly )
    RowWidth = clog2( k_ary )
    END = n_fly * RowWidth
    BEGIN = END - RowWidth

    # Interface

    s.get  = GetIfcRTL( PacketType )
    s.give = [ GiveIfcRTL(PacketType ) for _ in range ( s.num_outports ) ]
    s.pos  = InPort( PositionType )

    # Componets

    s.out_dir  = Wire( OutType )
    s.give_rdy = [ Wire() for _ in range( s.num_outports ) ]
    s.give_ens = Wire( mk_bits( s.num_outports ) )

    # Connections

    for i in range( s.num_outports ):
      s.give_ens[i] //= s.give[i].en
      s.give_rdy[i] //= s.give[i].rdy

    # Routing logic

    @update
    def up_ru_routing():
      for i in range( s.num_outports ):
        s.give_rdy[i] @= 0

      if s.get.rdy:
        s.out_dir @= s.get.ret.dst[BEGIN : END]
        s.give_rdy[ s.out_dir ] @= 1

    @update
    def up_ru_get_en():
      s.get.en @= s.give_ens > 0
      for i in range( s.num_outports ):
        s.give[i].ret @= s.get.ret
      if s.get.rdy:
        s.give[ s.out_dir ].ret.dst @= s.get.ret.dst << RowWidth

  # Line trace

  def line_trace( s ):
    out_str = [ "" for _ in range( s.num_outports ) ]
    for i in range (s.num_outports):
      out_str[i] = "{}".format( s.give[i] )

    return "{}({}){}".format( s.get, s.out_dir, "|".join( out_str ) )
