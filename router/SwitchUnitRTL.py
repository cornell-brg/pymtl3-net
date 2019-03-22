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
from pclib.rtl  import Mux, BypassQueue1RTL

from pclib.rtl.arbiters  import RoundRobinArbiterEn
from ocn_pclib.rtl.Encoder   import Encoder
#from pclib.ifcs.EnRdyIfc import InEnRdyIfc, OutEnRdyIfc
from pclib.ifcs.SendRecvIfc import *

class SwitchUnitRTL( RTLComponent ):
  def construct(s, PacketType, num_inports=5):

    # Constants
    s.num_inports = num_inports
    s.sel_width   = clog2( num_inports )

    # Interface
#    s.recv = [ InEnRdyIfc( PacketType ) for _ in range( s.num_inports ) ]
    s.recv = [ RecvIfcRTL( PacketType ) for _ in range( s.num_inports ) ]
    s.send = SendIfcRTL ( PacketType )

    # Components
    s.bypass_queue = [BypassQueue1RTL(PacketType) for _ in range(s.num_inports)]
    s.arbiter = RoundRobinArbiterEn( num_inports )
    s.encoder = Encoder( num_inports, s.sel_width )
    s.mux = Mux( PacketType, num_inports )

    # Connections
    s.connect( s.arbiter.grants, s.encoder.in_ )
    s.connect( s.encoder.out,    s.mux.sel     )
    s.connect( s.mux.out,        s.send.msg    )

    for i in range( num_inports ):
      s.connect( s.recv[i].en,  s.bypass_queue[i].enq.val )
      s.connect( s.recv[i].msg, s.bypass_queue[i].enq.msg )
      s.connect( s.recv[i].rdy, s.bypass_queue[i].enq.rdy )

      s.connect( s.bypass_queue[i].deq.val, s.arbiter.reqs[i] )
      s.connect( s.bypass_queue[i].deq.msg, s.mux.in_[i] )

    @s.update
    def enableArbiter():
      s.arbiter.en = s.arbiter.grants > 0 and s.send.rdy

    @s.update
    def enableSend():
      s.send.en = s.arbiter.grants > 0 and s.send.rdy
 
    @s.update
    def inRdy():
      for i in range( num_inports ):
        s.bypass_queue[i].deq.rdy = s.arbiter.grants[i] and s.send.rdy

  # TODO: implement line trace
  def line_trace( s ):
    recv_str = '[ '
    recv_rdy_str = '[ '
    bypass_queue_str = '['
    for i in range( s.num_inports ):
      recv_str = recv_str + str(s.recv[i].msg.payload) + ','
      recv_rdy_str = recv_rdy_str + str(s.recv[i].rdy) + ','
      bypass_queue_str += str(s.bypass_queue[i].deq.msg.payload) + ','
    recv_str = recv_str + ']'
    recv_rdy_str = recv_rdy_str + ']'
    bypass_queue_str += ']'
    return "{} (recv.rdy:{}; send.en:{}; send.rdy:{}, bq:{}) -> {}".format( recv_str, recv_rdy_str, s.send.en, s.send.rdy, bypass_queue_str, s.send.msg.payload )
