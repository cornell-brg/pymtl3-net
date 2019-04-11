#=========================================================================
# VCUnitGiveRTL.py
#=========================================================================
# An virtual channel unit with a recv/give interface. 
#
# Author : Yanghui Ou, Cheng Tan
#   Date : April 11, 2019

from pymtl            import *
from pclib.ifcs       import RecvIfcRTL
from pclib.ifcs       import GiveIfcRTL
from pclib.rtl.queues import NormalQueueRTL

class ULVCUnitRTL( Component ):

  def construct( s, PacketType, QueueType=NormalQueueRTL ):

    # Interface

    s.recv = RecvIfcRTL( PacketType )
    s.give = GiveIfcRTL( PacketType )

    # Component
    s.in_id  = Bits1 ( 0 )
    s.out_id = Bits1 ( 0 )
    s.upper  = QueueType( PacketType )
    s.lower  = QueueType( PacketType )
    s.arbiter = # TODO
    
    # Connections

#    s.connect( s.recv,          s.upper.enq )
#    s.connect( s.recv,          s.lower.enq )
#    s.connect( s.queue.deq.msg, s.give.msg  )
#    s.connect( s.queue.deq.en,  s.give.en   )
#    s.connect( s.queue.deq.rdy, s.give.rdy  )

    @s.update():
    def vcIn():
      if s.in_id == 0:
        s.upper.enq.en  = s.recv.en 
        s.upper.enq.rdy = s.recv.rdy
        s.upper.enq.msg = s.recv.msg
      else:
        s.lower.enq.en = s.recv.en 
        s.lower.enq.rdy = s.recv.rdy
        s.lower.enq.msg = s.recv.msg

    @s.update
    def vcOut():
      if s.out_id == 0:
        s.give.en  = s.upper.deq.en
        s.give.rdy = s.upper.deq.rdy
        s.give.msg = s.upper.deq.msg
      else:
        s.give.en  = s.lower.deq.en
        s.give.rdy = s.lower.deq.rdy
        s.give.msg = s.lower.deq.msg

    @s.update
    def vcInID():
      s.in_id = s.recv.msg.opaque

    @s.update
    def vcOutID():
      if s.arbiter.grants[0]:
        s.out_id = 0
      else:
        s.out_id = 1

  def line_trace( s ):
    return "{}({}){}".format( s.recv, s.queue.count, s.give )
