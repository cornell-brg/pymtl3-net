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
  def construct( s, PktType, QueueType=None, num_entries=2 ):

    # Constant
    s.QueueType = QueueType
#    s.num_entries = num_entries

    # Interface
    s.recv =  InEnRdyIfc( PktType )
    s.send = OutEnRdyIfc( PktType )

    if s.QueueType != None:
      # Component
      s.queue = s.QueueType(num_entries, Type=PktType)
      
      # Connections
      s.connect( s.recv.rdy, s.queue.enq.rdy )
#      s.connect( s.recv.en,  s.queue.enq.val )
#      s.connect( s.recv.msg, s.queue.enq.msg )
  
      @s.update
      def process():
        s.send.msg  = s.queue.deq.msg
        s.send.en   = s.send.rdy and s.queue.deq.val
        s.queue.deq.rdy = s.send.rdy

        if s.recv.en == 1:
          s.queue.enq.msg = s.recv.msg
          s.queue.enq.val = 1

    else:
      s.connect( s.recv, s.send )
  
  def line_trace( s ):
    if s.QueueType != None:
      return "{}({}){}".format( s.recv.msg, s.queue.ctrl.num_entries, 
            s.send.msg )
    else:
      return "{}(0){}".format( s.recv.msg, s.send.msg)
