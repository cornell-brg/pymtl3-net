#=========================================================================
# InputUnitFL.py
#=========================================================================
# An input unit in FL
#
# Author : Yanghui Ou, Cheng Tan
#   Date : May 13, 2019

from pymtl            import *
from pclib.ifcs       import RecvIfcRTL
from pclib.ifcs       import GiveIfcRTL
from pclib.rtl.queues import NormalQueueRTL

class InputUnitFL( Component ):

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
