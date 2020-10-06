"""
==========================================================================
OutputUnitValRdy.py
==========================================================================
RTL implementation of OutputUnit.

Author : Yanghui Ou
  Date : Oct 5, 2020
"""
from pymtl3 import *
from pymtl3.stdlib.ifcs import InValRdyIfc, OutValRdyIfc


class OutputUnitValRdy( Component ):

  def construct( s, PacketType, QueueType=None, data_gating=False ):

    # Interface
    s.in_ = InValRdyIfc ( PacketType )
    s.out = OutValRdyIfc( PacketType )

    s.QueueType = QueueType

    # If queue type is assigned
    if s.QueueType != None:

      # Component
      s.queue = QueueType( PacketType )
      s.queue.enq //= s.in_
      s.queue.deq //= s.out

    # No ouput queue
    else:

      if data_gating:
        s.out.msg //= lambda: s.in_.msg if s.out.val else PacketType()
      else:
        s.out.msg //= lambda: s.in_.msg

      s.out.val //= s.in_.val
      s.out.rdy //= s.in_.rdy

  def line_trace( s ):
    if s.QueueType != None:
      return "{}({}){}".format( s.in_, s.queue.count, s.out )
    else:
      return "{}(0){}".format( s.in_, s.out)
