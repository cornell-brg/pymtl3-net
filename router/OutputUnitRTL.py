#=========================================================================
# OutputUnitRTL.py
#=========================================================================
# An Output unit of the router. Just one normal queue, no credit.
# Note that the interface is send/recv-based.
# Enabling parameter passing.
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Feb 28, 2019

from pymtl import *
from pclib.ifcs.EnRdyIfc  import InEnRdyIfc, OutEnRdyIfc

class OutputUnitRTL( RTLComponent ):
  def construct( s, PacketType, QueueType=None ):
    
    # Interface
    s.recv =  InEnRdyIfc( PacketType )
    s.send = OutEnRdyIfc( PacketType )
    s.QueueType = QueueType

    # If no queue type is assigned
    if s.QueueType != None:

      # Component
      s.queue = s.QueueType( Type=PacketType ) 
  
      # Connections
      s.connect( s.recv.rdy, s.queue.enq.rdy )
      s.connect( s.recv.en,  s.queue.enq.val )
      s.connect( s.recv.msg, s.queue.enq.msg )

      s.connect( s.send.msg, s.queue.deq.msg )
  
      @s.update
      def enSend():
        s.send.en   = s.send.rdy and s.queue.deq.val
        s.queue.deq.rdy = s.send.rdy

    # No ouput queue
    else:
      s.connect( s.recv, s.send ) 

  def line_trace( s ):
    if s.QueueType != None:
      return "{}({}){}".format( s.recv.msg, s.queue.ctrl.num_entries,
            s.send.msg )
    else:
      return "{}(0){}".format( s.recv.msg, s.send.msg)
