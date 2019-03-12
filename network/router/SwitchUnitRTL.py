#=========================================================================
# SwitchUnit.py
#=========================================================================
# A simple switch unit that supports single-phit packet.
# Note that the interface is send/recv-based.
# Enabling parameter passing.
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Feb 28, 2019

from pymtl      import *
from pclib.ifcs import InValRdyIfc, OutValRdyIfc
from pclib.rtl  import Mux

from ocn_pclib.Arbiters  import RoundRobinArbiterEn
from ocn_pclib.Encoder   import Encoder
from pclib.ifcs.EnRdyIfc import InEnRdyIfc, OutEnRdyIfc

class SwitchUnitRTL( RTLComponent ):
  def construct( s, msg_type, num_inports ):

    # Constants
    s.num_inports = num_inports
    s.sel_width   = clog2( num_inports )

    # Interface
#    s.in_ =  InValRdyIfc[ s.num_inports ]( msg_type )
#    s.out = OutValRdyIfc ( msg_type )

    s.recv = [ InEnRdyIfc( msg_type ) for _ in range( s.num_inports ) ]
    s.send = OutEnRdyIfc ( msg_type )

    # Components
    s.arbiter = RoundRobinArbiterEn( num_inports )
    s.encoder = Encoder( num_inports, s.sel_width )
    s.mux = Mux( msg_type, num_inports )
#    s.random_wire = Wire ( Bits5 )

    # Connections
    s.connect( s.arbiter.grants, s.encoder.in_ )
#    s.connect( s.arbiter.grants, s.random_wire )
    s.connect( s.encoder.out,    s.mux.sel     )
    s.connect( s.mux.out,        s.send.msg    )

    for i in range( num_inports ):
#      s.connect( s.in_[i].msg, s.mux.in_[i]      )
#      s.connect( s.in_[i].val, s.arbiter.reqs[i] )
      s.connect( s.recv[i].msg, s.mux.in_[i]      )
#      s.connect( s.recv[i].en, s.arbiter.reqs[i] )

    @s.update
    def enableArbiter():
#      s.arbiter.en = (s.arbiter.grants > 0) and s.send.rdy
#      s.arbiter.en = (s.arbiter.grants > 0) and s.send.rdy
      s.arbiter.en   = Bits1( 1 )
      s.arbiter.reqs = Bits5( 0b11111 )
      s.send.en = Bits1( 1 )
 
    @s.update
    def inRdy():
      for i in range( num_inports ):
#        s.in_[i].rdy.value = s.arbiter.grants[i] and s.out.rdy
        s.recv[i].rdy = s.arbiter.grants[i] and s.send.rdy
 
  # TODO: implement line trace
  def line_trace( s ):

    recv_str = '[ '
    for i in range( s.num_inports ):
      recv_str = recv_str + str(s.recv[i].msg) + ', '
    recv_str = recv_str + ']'
    return "{} (s.send.en:{}; s.send.rdy:{}, s.arbiter.grants:{}, "\
      "s.arbiter.reqs:{}, s.mux.in:{}, s.mux.sel:{}) {}".format( 
      recv_str, s.send.en, s.send.rdy, s.arbiter.grants, s.arbiter.reqs, 
      s.mux.in_, s.mux.sel, s.send.msg )
