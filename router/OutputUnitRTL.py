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
      s.connect( s.get.msg,       s.queue.enq.msg )
      s.connect( s.queue.deq.msg, s.send.msg      )

      @s.update
      def up_get_deq():
        s.get.en       = s.get.rdy & s.queue.enq.rdy
        s.queue.enq.en = s.get.rdy & s.queue.enq.rdy

      @s.update
      def up_deq_send():
        s.send.en      = s.send.rdy & s.queue.deq.rdy
        s.queue.deq.en = s.send.rdy & s.queue.deq.rdy

    # No ouput queue
    else:

      s.connect( s.get.msg, s.send.msg )

      @s.update
      def up_get_send():
        s.get.en  = s.get.rdy & s.send.rdy
        s.send.en = s.get.rdy & s.send.rdy

  def line_trace( s ):
    if s.QueueType != None:
      return "{}({}){}".format( s.get, s.queue.count, s.send )
    else:
      return "{}(0){}".format( s.get, s.send)
