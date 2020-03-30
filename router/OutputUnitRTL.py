"""
==========================================================================
OutputUnitRTL.py
==========================================================================
RTL implementation of OutputUnit.

Author : Yanghui Ou, Cheng Tan
  Date : Feb 28, 2019
"""
from pymtl3 import *
from pymtl3.stdlib.ifcs import GetIfcRTL, SendIfcRTL
from pymtl3.stdlib.rtl.queues import NormalQueueRTL


class OutputUnitRTL( Component ):
  def construct( s, PacketType, QueueType=None ):

    # Interface
    s.get  = GetIfcRTL ( PacketType )
    s.send = SendIfcRTL( PacketType )

    s.QueueType = QueueType

    # If no queue type is assigned
    if s.QueueType != None:

      # Component
      s.queue = QueueType( PacketType )

      # Connections
      s.get.ret       //= s.queue.enq.msg
      s.queue.deq.ret //= s.send.msg

      @update
      def up_get_deq():
        both_rdy = s.get.rdy & s.queue.enq.rdy
        s.get.en       @= both_rdy
        s.queue.enq.en @= both_rdy

      @update
      def up_deq_send():
        both_rdy = s.send.rdy & s.queue.deq.rdy
        s.send.en      @= both_rdy
        s.queue.deq.en @= both_rdy

    # No ouput queue
    else:

      s.get.ret //= s.send.msg

      @update
      def up_get_send():
        both_rdy = s.get.rdy & s.send.rdy
        s.get.en  @= both_rdy
        s.send.en @= both_rdy

  def line_trace( s ):
    if s.QueueType != None:
      return "{}({}){}".format( s.get, s.queue.count, s.send )
    else:
      return "{}(0){}".format( s.get, s.send)
