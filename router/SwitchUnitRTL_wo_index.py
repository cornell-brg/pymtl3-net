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

    @s.update
    def up_arb_send_en():
      s.arbiter.en = s.arbiter.grants > Bits5(0) and s.send.rdy
      s.send.en = s.arbiter.grants > Bits5(0) and s.send.rdy

    @s.update
    def up_get_en():
      s.get[0].en = (
        Bits1(1) if s.get[0].rdy and s.send.rdy and s.mux.sel==Bits3(0) else 
        Bits1(0)
      ) 
      s.get[1].en = (
        Bits1(1) if s.get[1].rdy and s.send.rdy and s.mux.sel==Bits3(1) else 
        Bits1(0)
      ) 
      s.get[2].en = (
        Bits1(1) if s.get[2].rdy and s.send.rdy and s.mux.sel==Bits3(2) else 
        Bits1(0)
      ) 
      s.get[3].en = (
        Bits1(1) if s.get[3].rdy and s.send.rdy and s.mux.sel==Bits3(3) else 
        Bits1(0)
      ) 
      s.get[4].en = (
        Bits1(1) if s.get[4].rdy and s.send.rdy and s.mux.sel==Bits3(4) else 
        Bits1(0)
      ) 

  def line_trace( s ):

    in_trace = [ "" for _ in range( s.num_inports ) ]
    for i in range( s.num_inports ):
      in_trace[i] = "{}".format( s.get[i] )

    return "{}(){}".format( "|".join( in_trace ), s.send )
