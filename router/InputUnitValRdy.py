"""
=========================================================================
InputUnitValRdy.py
=========================================================================
An input unit with val/rdy interface.

Author : Yanghui Ou
  Date : Oct 5, 2020
"""
from pymtl3 import *
# from pymtl3.stdlib.ifcs import GiveIfcRTL, RecvIfcRTL
# from pymtl3.stdlib.queues import NormalQueueRTL
from pymtl3.stdlib.ifcs import InValRdyIfc, OutValRdyIfc

from ocnlib.rtl.valrdy_queues import NormalQueueRTL


class InputUnitValRdy( Component ):

  def construct( s, PacketType, QueueType = NormalQueueRTL ):

    # Interface

    s.in_ = InValRdyIfc ( PacketType )
    s.out = OutValRdyIfc( PacketType )

    # Component

    s.queue = QueueType( PacketType )
    s.queue.enq //= s.in_
    s.queue.deq //= s.out

  def line_trace( s ):
    return f"{s.in_}({s.queue.count}){s.out}"
