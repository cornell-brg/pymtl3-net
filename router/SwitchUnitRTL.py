#=========================================================================
# SwitchUnitRTL.py
#=========================================================================
# A switch unit with GetIfcRTL and SendIfcRTL.
#
# Author : Yanghui Ou, Cheng Tan
#   Date : Feb 28, 2019

from pymtl3 import *
from pymtl3.stdlib.rtl          import Mux
from pymtl3.stdlib.rtl.arbiters import RoundRobinArbiterEn
from ocn_pclib.rtl.Encoder import Encoder
from pymtl3.stdlib.ifcs    import GetIfcRTL, SendIfcRTL

class SwitchUnitRTL( Component ):

  def construct( s, PacketType, num_inports=5 ):

    # Constants

    s.num_inports = num_inports
    s.sel_width   = clog2( num_inports )

    # Interface

    s.get  = [ GetIfcRTL( PacketType ) for _ in range( s.num_inports ) ]
    s.send = SendIfcRTL( PacketType )

    # Components

    s.get_en  = [ Wire( Bits1 ) for _ in range( s.num_inports ) ]
    s.get_rdy = [ Wire( Bits1 ) for _ in range( s.num_inports ) ]

    s.arbiter = RoundRobinArbiterEn( num_inports )

    s.mux = Mux( PacketType, num_inports )(
      out = s.send.msg
    )

    s.encoder = Encoder( num_inports, s.sel_width )(
      in_ = s.arbiter.grants,
      out = s.mux.sel
    )

    # Connections

    for i in range( num_inports ):
      s.connect( s.get[i].rdy, s.arbiter.reqs[i] )
      s.connect( s.get[i].msg, s.mux.in_[i]      )
      s.connect( s.get[i].en,  s.get_en[i]       )
      s.connect( s.get[i].rdy, s.get_rdy[i]      )

    @s.update
    def up_arb_send_en():
      s.arbiter.en = s.arbiter.grants > Bits5(0) and s.send.rdy
      s.send.en = s.arbiter.grants > Bits5(0) and s.send.rdy

    @s.update
    def up_get_en():
      for i in range( num_inports ):
        s.get_en[i] = (
          Bits1(1) if s.get_rdy[i] and s.send.rdy and s.mux.sel==Bits3(i) else 
          Bits1(0)
        )

  def line_trace( s ):

    in_trace = [ "" for _ in range( s.num_inports ) ]
    for i in range( s.num_inports ):
      in_trace[i] = "{}".format( s.get[i] )

    return "{}(){}".format( "|".join( in_trace ), s.send )
