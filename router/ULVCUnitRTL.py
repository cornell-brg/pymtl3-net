#=========================================================================
# VCUnitGiveRTL.py
#=========================================================================
# An virtual channel unit with a recv/give interface. 
#
# Author : Yanghui Ou, Cheng Tan
#   Date : April 11, 2019

from pymtl              import *
from pclib.ifcs         import RecvIfcRTL
from pclib.ifcs         import GiveIfcRTL
from pclib.rtl.arbiters import RoundRobinArbiterEn
from pclib.rtl.queues   import NormalQueueRTL

class ULVCUnitRTL( Component ):

  def construct( s, PacketType, QueueType=NormalQueueRTL ):

    # Interface

    s.recv = RecvIfcRTL( PacketType )
    s.give = GiveIfcRTL( PacketType )

    # Component
    s.upper  = QueueType( PacketType )
    s.lower  = QueueType( PacketType )
    s.arbiter = RoundRobinArbiterEn( 2 ) 
    
    # Connections

    s.connect( s.arbiter.reqs[0], s.upper.deq.rdy )
    s.connect( s.arbiter.reqs[1], s.lower.deq.rdy )

    @s.update
    def vcIn():
      if s.recv.msg.opaque == 0:
        s.upper.enq.en  = s.recv.en 
        s.recv.rdy = s.upper.enq.rdy
        s.upper.enq.msg = s.recv.msg
        s.lower.enq.en  = 0
      else:
        s.lower.enq.en = s.recv.en 
        s.recv.rdy = s.lower.enq.rdy
        s.lower.enq.msg = s.recv.msg
        s.upper.enq.en  = 0

    @s.update
    def vcOut():
      if s.arbiter.grants[0]:
        s.upper.deq.en = s.give.en
        s.give.rdy = s.upper.deq.rdy
        s.give.msg = s.upper.deq.msg
        s.lower.deq.en = 0

      elif s.arbiter.grants[1]:
        s.lower.deq.en = s.give.en
        s.give.rdy = s.lower.deq.rdy
        s.give.msg = s.lower.deq.msg
        s.upper.deq.en = 0

    @s.update
    def up_arb_en():
      s.arbiter.en = s.arbiter.grants > 0 and s.give.rdy

  def line_trace( s ):
    return "{}({},{}->{},{}){}".format( s.recv, s.upper.enq.msg.payload, 
      s.lower.enq.msg.payload, s.upper.deq.msg.payload, 
      s.lower.deq.msg.payload, s.give )
