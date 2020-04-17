'''
==========================================================================
XbarRouteUnitRTL
==========================================================================
Route unit for single-flit xbar.

Author : Yanghui Ou
  Date : Apr 16, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs import GetIfcRTL, GiveIfcRTL

class XbarRouteUnitRTL( Component ):

  def construct( s, PacketType, num_outports ):

    # Local parameters

    dir_nbits = 1 if num_outports==1 else clog2( num_outports )
    DirT      = mk_bits( dir_nbits )
    BitsN     = mk_bits( num_outports )

    # Interface

    s.get  = GetIfcRTL( PacketType )
    s.give = [ GiveIfcRTL( PacketType ) for _ in range( num_outports ) ]

    # Componets

    s.out_dir  = Wire( DirT  )
    s.give_ens = Wire( BitsN )

    # Connections

    for i in range( num_outports ):
      s.get.ret     //= s.give[i].ret
      s.give_ens[i] //= s.give[i].en

    # Routing logic

    @s.update
    def up_ru_routing():
      s.out_dir = DirT( s.get.ret.dst )

      for i in range( num_outports ):
        s.give[i].rdy = b1(0)

      if s.get.rdy:
        s.give[ s.out_dir ].rdy = b1(1)

    @s.update
    def up_ru_give_en():
      s.get.en = s.give_ens > BitsN(0)

  # Line trace
  def line_trace( s ):
    out_str = "|".join([ str(x) for x in s.give ])
    return f"{s.get}({s.out_dir}){out_str}"
