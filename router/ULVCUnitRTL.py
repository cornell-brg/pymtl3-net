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

    # Constants
    UPPER = 0
    LOWER = 1

    # Interface

    s.recv = RecvIfcRTL( PacketType )
    s.give = GiveIfcRTL( PacketType )

    # Component
    s.upper  = QueueType( PacketType )
    s.lower  = QueueType( PacketType )
    s.arbiter = RoundRobinArbiterEn( 2 ) 
    
    # Connections

    s.connect( s.arbiter.reqs[ UPPER ], s.upper.deq.rdy )
    s.connect( s.arbiter.reqs[ LOWER ], s.lower.deq.rdy )
    s.connect( s.upper.enq.msg,   s.recv.msg      )
    s.connect( s.lower.enq.msg,   s.recv.msg      )

    @s.update
    def set_recv_rdy():
      s.recv.rdy = ( s.upper.enq.rdy and ( s.upper.enq.msg.opaque == UPPER ) ) or\
                   ( s.lower.enq.rdy and ( s.lower.enq.msg.opaque == LOWER ) )

    @s.update
    def set_enq_en():
      s.upper.enq.en = s.recv.en and ( s.upper.enq.msg.opaque == UPPER )
      s.lower.enq.en = s.recv.en and ( s.lower.enq.msg.opaque == LOWER )

    @s.update
    def set_give_rdy():
      s.give.rdy = ( ( s.upper.deq.rdy and s.arbiter.grants[ UPPER ] ) ) or\
                   ( ( s.lower.deq.rdy and s.arbiter.grants[ LOWER ] ) )

    @s.update
    def set_give_msg():
      if s.arbiter.grants[ UPPER ]:
        s.give.msg = s.upper.deq.msg
      elif s.arbiter.grants[ LOWER ]:
        s.give.msg = s.lower.deq.msg

    @s.update
    def set_deq_en():
      s.upper.deq.en = s.give.en and s.arbiter.grants[ UPPER ]
      s.lower.deq.en = s.give.en and s.arbiter.grants[ LOWER ]

    @s.update
    def up_arb_en():
      s.arbiter.en = s.arbiter.grants > 0 and s.give.en

  def line_trace( s ):
    return "{}({},{}->{},{}){}".format( s.recv, s.upper.enq.msg.payload, 
      s.lower.enq.msg.payload, s.upper.deq.msg.payload, 
      s.lower.deq.msg.payload, s.give )
