"""
=========================================================================
SwitchUnitRTL.py
=========================================================================
A switch unit with GetIfcRTL and SendIfcRTL.

Author : Yanghui Ou, Cheng Tan
  Date : Feb 28, 2019
"""
from pymtl3 import *
from pymtl3.stdlib.ifcs import GetIfcRTL, GiveIfcRTL, SendIfcRTL
from pymtl3.stdlib.basic_rtl import Mux, RoundRobinArbiterEn, Encoder


class SwitchUnitRTL( Component ):

  def construct( s, PacketType, num_inports=5 ):

    # Local parameters

    s.num_inports = num_inports
    s.sel_width   = clog2( num_inports )
    GrantType     = mk_bits( num_inports )
    SelType       = mk_bits( s.sel_width )
    s.set_ocp = 0
    s.clear_ocp = 0

    # Interface

    s.get  = [ GetIfcRTL( PacketType ) for _ in range( s.num_inports ) ]
    s.give = GiveIfcRTL( PacketType )
    s.out_ocp = OutPort( Bits1 )

    # Components

    s.get_en  = [ Wire( Bits1 ) for _ in range( s.num_inports ) ]
    s.get_rdy = [ Wire( Bits1 ) for _ in range( s.num_inports ) ]

    s.arbiter = RoundRobinArbiterEn( num_inports )
    s.arbiter.en //= 1
    s.mux = Mux( PacketType, num_inports )
    s.mux.out //= s.give.ret

    s.encoder = Encoder( num_inports, s.sel_width )
    s.encoder.in_ //= s.arbiter.grants
    s.encoder.out //= s.mux.sel

    # Connections

    for i in range( num_inports ):
      s.get[i].rdy //= s.arbiter.reqs[i]
      s.get[i].ret //= s.mux.in_[i]
      s.get[i].en  //= s.get_en[i]
      s.get[i].rdy //= s.get_rdy[i]

    @update
    def up_give():
      s.give.rdy @= s.arbiter.grants > GrantType(0)

    @update
    def up_get_en():
      for i in range( num_inports ):
        s.get_en[i] @= s.give.en & ( s.mux.sel==SelType(i) )

  # Line trace

  def line_trace( s ):
    in_trace = [ str(s.get[i]) for i in range( s.num_inports ) ]
    return "{}(){}".format( "|".join( in_trace ), s.give )
