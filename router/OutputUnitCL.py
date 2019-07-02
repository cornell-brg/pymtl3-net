#=========================================================================
# OutputUnitCL.py
#=========================================================================
# Cycle level implementation of output unit.
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Feb 28, 2019

from pymtl3 import *

class OutputUnitCL( Component ):

  def construct( s, PacketType, QueueType = None ):

    # Interface
    s.get  = NonBlockingCallerIfc( PacketType )
    s.send = NonBlockingCallerIfc( PacketType )
    s.QueueType = QueueType

    # If no queue type is assigned
    if s.QueueType != None:
      # Component
      s.queue = QueueType()

      @s.update
      def up_ou_get_enq():
        if s.get.rdy() and s.queue.enq.rdy():
          s.queue.enq( s.get() )

      @s.update
      def up_ou_deq_send():
        if s.queue.deq.rdy() and s.send.rdy():
          s.send( s.queue.deq() )

    # No ouput queue
    else:
      @s.update
      def up_ou_get_send():
        if s.get.rdy() and s.send.rdy():
          s.send( s.get() )

  def line_trace( s ):
    return "{}(){}".format( s.get, s.send )
