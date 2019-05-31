#=========================================================================
# InputUnitGiveRTL.py
#=========================================================================
# An input unit with a recv interface as input and give interface as 
# output.
#
# Author : Yanghui Ou, Cheng Tan
#   Date : Mar 23, 2019

from pymtl3            import *
from pymtl3.stdlib.ifcs       import RecvIfcRTL
from pymtl3.stdlib.ifcs       import GiveIfcRTL
from pymtl3.stdlib.rtl.queues import NormalQueueRTL

class InputUnitRTL( Component ):

  def construct( s, PacketType, QueueType = NormalQueueRTL ):

    # Interface

    s.recv = RecvIfcRTL( PacketType )
    s.give = GiveIfcRTL( PacketType )

    # Component

    s.queue = QueueType( PacketType )
    
    # Connections

    s.connect( s.recv,          s.queue.enq )
    s.connect( s.queue.deq.msg, s.give.msg  )
    s.connect( s.queue.deq.en,  s.give.en   )
    s.connect( s.queue.deq.rdy, s.give.rdy  )

  def line_trace( s ):
    return "{}({}){}".format( s.recv, s.queue.count, s.give )
