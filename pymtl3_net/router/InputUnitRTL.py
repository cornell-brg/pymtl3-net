"""
=========================================================================
InputUnitGiveRTL.py
=========================================================================
An input unit with a recv interface as input and give interface as output.

Author : Yanghui Ou, Cheng Tan
  Date : Mar 23, 2019
"""
from pymtl3 import *
from pymtl3.stdlib.ifcs import GiveIfcRTL, RecvIfcRTL
from pymtl3.stdlib.queues import NormalQueueRTL


class InputUnitRTL( Component ):

  def construct( s, PacketType, QueueType = NormalQueueRTL ):

    # Interface

    s.recv = RecvIfcRTL( PacketType )
    s.give = GiveIfcRTL( PacketType )

    # Component

    s.queue = QueueType( PacketType )
    s.queue.enq //= s.recv
    s.queue.deq //= s.give

  def line_trace( s ):
    return f"{s.recv}({s.queue.count}){s.give}"
