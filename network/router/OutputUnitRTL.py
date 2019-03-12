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
  def construct( s, pkt_type, QueueType=None ):
    
    # Interface
    s.recv =  InEnRdyIfc( pkt_type )
    s.send = OutEnRdyIfc( pkt_type )

    # If no queue type is assigned
    if QueueType != None:

      # Component
      # s.queue = NormalQueue( num_entries, pkt_type ) 
      s.queue = QueueType( Type=pkt_type ) 
  
      # Connections
      s.connect( s.recv.rdy, s.queue.enq.rdy )
      s.connect( s.recv.en,  s.queue.enq.val )
      s.connect( s.recv.msg, s.queue.enq.msg )
  
      @s.update
      def proceed():
        s.send.msg  = s.queue.deq.msg
        s.send.en   = s.send.rdy and s.queue.deq.val
        s.queue.deq.rdy = s.send.rdy
      
    # No ouput queue
    else:
      s.connect( s.recv, s.send ) 

  def line_trace( s ):
    return "{} || {}".format( s.recv.msg, s.send.msg )
