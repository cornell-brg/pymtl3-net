"""
=========================================================================
InputUnitRTL.py
=========================================================================
An input unit with val/rdy stream interfaces.

Author : Yanghui Ou, Cheng Tan
  Date : Mar 23, 2019
"""
from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import OStreamIfc, IStreamIfc
from pymtl3.stdlib.stream import StreamNormalQueue


class InputUnitRTL( Component ):

  def construct( s, PacketType, QueueType=StreamNormalQueue ):

    # Interface

    s.recv = IStreamIfc( PacketType )
    s.send = OStreamIfc( PacketType )

    # Component

    s.queue = QueueType( PacketType )
    s.queue.istream //= s.recv
    s.queue.ostream //= s.send

  def line_trace( s ):
    return f"{s.recv}({s.queue.count}){s.send}"
