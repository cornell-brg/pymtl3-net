#=========================================================================
# SwitchUnitGetRTL.py
#=========================================================================
# A switch unit with GetIfcRTL and SendIfcRTL.
#
# Author : Yanghui Ou, Cheng Tan
#   Date : Feb 28, 2019

from pymtl                 import *
from pclib.rtl             import Mux
from pclib.rtl.arbiters    import RoundRobinArbiterEn
from ocn_pclib.rtl.Encoder import Encoder
from ocn_pclib.ifcs        import GetIfcRTL
from pclib.ifcs            import SendIfcRTL

class SwitchUnitGetRTL( ComponentLevel6 ):

  def construct( s, PacketType, num_inports=5 ):

    # Constants

    s.num_inports = num_inports
    s.sel_width   = clog2( num_inports )

    # Interface

    s.recv = [ GetIfcRTL( PacketType ) for _ in range( s.num_inports ) ]
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
      s.connect( s.recv[i].rdy, s.arbiter.reqs[i] )
      s.connect( s.recv[i].msg, s.mux.in_[i]      )

    @s.update
    def up_arb_send_en():
      s.arbiter.en = s.arbiter.grants > 0 and s.send.rdy
      s.send.en = s.arbiter.grants > 0 and s.send.rdy
 
    @s.update
    def up_recv_en():
      for i in range( num_inports ):
        s.recv[i].en = 1 if s.send.rdy and s.mux.sel==i else 0

  def line_trace( s ):

    in_trace = [ "" for _ in range( s.num_inports ) ]
    for i in range( s.num_inports ):
      in_trace[i] = "{}".format( s.recv[i] )

    return "{}(){}".format( "|".join( in_trace ), s.send )
