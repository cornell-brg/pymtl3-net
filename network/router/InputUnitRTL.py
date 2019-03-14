#=========================================================================
# InputUnitRTL.py
#=========================================================================
# An input unit for the router that supports single-phit packet.
# Note that the interface is send/recv-based.
# Enabling parameter passing.
#
# Author : Yanghui Ou, Cheng Tan
#   Date : Feb 23, 2019

from pymtl import *
from pclib.ifcs.EnRdyIfc  import InEnRdyIfc, OutEnRdyIfc
from pclib.rtl  import NormalQueueRTL

class InputUnitRTL( RTLComponent ):
  def construct( s, PktType, QueueType=None ):

    # Interface
    s.recv =  InEnRdyIfc( PktType )
    s.send = OutEnRdyIfc( PktType )
    s.QueueType = QueueType

    if s.QueueType != None:
      # Component
#      s.queue_entries = num_entries
      s.queue = s.QueueType( Type=PktType )
      
      # Connections
      s.connect( s.recv.rdy, s.queue.enq.rdy )
      s.connect( s.recv.en,  s.queue.enq.val )
      s.connect( s.recv.msg, s.queue.enq.msg )
  
      @s.update
      def process():
        s.send.msg  = s.queue.deq.msg
        s.send.en   = s.send.rdy and s.queue.deq.val
        s.queue.deq.rdy = s.send.rdy
    else:
      s.connect( s.recv, s.send )
  
  def line_trace( s ):
    if s.QueueType != None:
      return "{}({}){}".format( s.recv.msg, s.queue.ctrl.num_entries, 
            s.send.msg )
    else:
      return "{}(0){}".format( s.recv.msg, s.send.msg)
