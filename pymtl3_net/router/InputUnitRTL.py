"""
=========================================================================
InputUnitRTL.py
=========================================================================
An input unit with val/rdy stream interfaces.

Author : Yanghui Ou, Cheng Tan
  Date : Mar 23, 2019
"""
from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import SendIfcRTL, RecvIfcRTL
from pymtl3.stdlib.stream.queues import NormalQueueRTL


class InputUnitRTL( Component ):

  def construct( s, PacketType, QueueType=NormalQueueRTL ):

    # Interface

    s.recv = RecvIfcRTL( PacketType )
    s.send = SendIfcRTL( PacketType )

    # Component

    s.queue = QueueType( PacketType )
    s.queue.recv //= s.recv
    s.queue.send //= s.send

  def line_trace( s ):
    return f"{s.recv}({s.queue.count}){s.send}"
