#=========================================================================
# InputUnitStrFwdRTL.py
#=========================================================================
# An input unit with a recv interface as input and give interface as 
# output.
#
# Author : Cheng Tan, Yanghui Ou
#   Date : July 11, 2019

from pymtl3            import *
from pymtl3.stdlib.ifcs       import RecvIfcRTL
from pymtl3.stdlib.ifcs       import GiveIfcRTL
from pymtl3.stdlib.rtl.queues import NormalQueueRTL

class InputUnitStrFwdRTL( Component ):

  def construct( s, MsgType, QueueType = NormalQueueRTL ):

    # Interface

    s.recv = RecvIfcRTL( MsgType )
    s.give = GiveIfcRTL( MsgType )

    # Component

    s.queue = QueueType( MsgType )
    
    # Connections

    s.recv          //= s.queue.enq
    s.queue.deq.msg //= s.give.msg
    s.queue.deq.en  //= s.give.en
    s.queue.deq.rdy //= s.give.rdy

  def line_trace( s ):
    return "{}({}){}".format( s.recv, s.queue.count, s.give )
