#=========================================================================
# LinkUnitRTL.py
#=========================================================================
# A Link unit for connecting routers to form network.
#
# Author : Cheng Tan
#   Date : Mar 16, 2019

from pymtl import *
from pclib.ifcs.EnRdyIfc  import InEnRdyIfc, OutEnRdyIfc
from pclib.rtl  import NormalQueueRTL

class LinkUnitRTL( RTLComponent ):
  def construct(s, PktType, QueueType=None, num_stages=2, num_entries=2):

    # Constant
    s.QueueType   = QueueType
    s.num_stages  = num_stages 
    s.num_entries = num_entries

    # Interface
    s.recv  =  InEnRdyIfc( PktType )
    s.send  = OutEnRdyIfc( PktType )

    if s.QueueType != None and s.num_stages != 0:
      # Component
      s.queues = [s.QueueType(s.num_entries, Type = PktType) 
                   for _ in range (s.num_stages)]

      # Connections
      s.connect( s.recv.rdy, s.queues[0].enq.rdy )
#      s.connect( s.recv.en,  s.queues[0].enq.val )
#      s.connect( s.recv.msg, s.queues[0].enq.msg )

      @s.update
      def process():
        last = s.num_stages - 1
        for i in range(s.num_stages - 1):
          s.queues[i+1].enq.msg = s.queues[i].deq.msg
          if s.queues[i].deq.val == 1:
            s.queues[i].deq.rdy = s.queues[i+1].enq.rdy
          s.queues[i+1].enq.val = s.queues[i].deq.rdy and s.queues[i].deq.val

        # recv is enabled only when the enq is ready!
        s.queues[0].enq.msg = s.recv.msg
        s.queues[0].enq.val = s.recv.en

        s.send.msg  = s.queues[last].deq.msg
        s.send.en   = s.send.rdy and s.queues[last].deq.val
        s.queues[last].deq.rdy = s.send.rdy and s.queues[last].deq.val

    else:
      s.connect(s.recv, s.send)

  def line_trace( s ):
    if s.QueueType != None and s.num_stages != 0:
      return "{}({}){}".format(s.recv.msg, s.num_stages, s.send.msg)
    else:
      return "{}(0){}".format( s.recv.msg, s.send.msg)

