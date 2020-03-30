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
from pymtl3.stdlib.rtl import Mux
from pymtl3.stdlib.rtl.arbiters import RoundRobinArbiterEn
from pymtl3.stdlib.rtl.Encoder import Encoder


class SwitchUnitRTL( Component ):

  def construct( s, PacketType, num_inports=5 ):

    # Local parameters

    s.num_inports = num_inports
    s.sel_width   = clog2( num_inports )
    s.set_ocp = 0
    s.clear_ocp = 0

    # Interface

    s.get  = [ GetIfcRTL( PacketType ) for _ in range( s.num_inports ) ]
    s.give = GiveIfcRTL( PacketType )
    s.out_ocp = OutPort()

    # Components

    s.get_en  = [ Wire() for _ in range( s.num_inports ) ]
    s.get_rdy = [ Wire() for _ in range( s.num_inports ) ]

    s.arbiter = RoundRobinArbiterEn( num_inports )
    s.arbiter.en //= 1

    s.mux = Mux( PacketType, num_inports )
    s.mux.out //= s.give.ret

    s.encoder = m = Encoder( num_inports, s.sel_width )
    m.in_ //= s.arbiter.grants
    m.out //= s.mux.sel

    # Connections

    for i in range( num_inports ):
      s.get[i].rdy //= s.arbiter.reqs[i]
      s.get[i].ret //= s.mux.in_[i]
      s.get[i].en  //= s.get_en[i]
      s.get[i].rdy //= s.get_rdy[i]

    @update
    def up_give():
      s.give.rdy @= s.arbiter.grants > 0

    @update
    def up_get_en():
      for i in range( num_inports ):
        s.get_en[i] @= s.give.en & ( s.mux.sel == i )

  # Line trace

  def line_trace( s ):
    in_trace = [ str(s.get[i]) for i in range( s.num_inports ) ]
    return "{}(){}".format( "|".join( in_trace ), s.give )
