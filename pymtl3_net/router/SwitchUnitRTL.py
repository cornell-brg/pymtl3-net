"""
=========================================================================
SwitchUnitRTL.py
=========================================================================
A switch unit with GetIfcRTL and SendIfcRTL.

Author : Yanghui Ou, Cheng Tan
  Date : Feb 28, 2019
"""
from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import SendIfcRTL, RecvIfcRTL
from pymtl3.stdlib.basic_rtl import Mux
from pymtl3.stdlib.basic_rtl import RoundRobinArbiterEn
from pymtl3.stdlib.basic_rtl import Encoder


class SwitchUnitRTL( Component ):

  def construct( s, PacketType, num_inports=5 ):

    # Local parameters

    s.num_inports = num_inports
    s.sel_width   = clog2( num_inports )

    # Interface

    s.recv = [ RecvIfcRTL( PacketType ) for _ in range( s.num_inports ) ]
    s.send = SendIfcRTL( PacketType )

    # Components

    s.arbiter = RoundRobinArbiterEn( num_inports )
    s.arbiter.en //= 1

    s.mux = Mux( PacketType, num_inports )
    s.mux.out //= s.send.msg

    s.encoder = Encoder( num_inports, s.sel_width )
    s.encoder.in_ //= s.arbiter.grants
    s.encoder.out //= s.mux.sel

    # Connections

    for i in range( num_inports ):
      s.recv[i].val //= s.arbiter.reqs[i]
      s.recv[i].msg //= s.mux.in_[i]

    @update
    def up_send_val():
      s.send.val @= s.arbiter.grants > 0

    # TODO: assert at most one rdy bit
    @update
    def up_get_en():
      for i in range( num_inports ):
        s.recv[i].rdy @= s.send.rdy & ( s.mux.sel == i )

  # Line trace

  def line_trace( s ):
    in_trace = [ str(s.recv[i]) for i in range( s.num_inports ) ]
    return "{}(){}".format( "|".join( in_trace ), s.send )

