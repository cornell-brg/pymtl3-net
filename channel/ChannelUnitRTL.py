#=========================================================================
# ChannelUnitRTL.py
#=========================================================================
# A Link unit for connecting routers to form network.
#
# Author : Cheng Tan
#   Date : Mar 16, 2019

from pymtl import *
from pclib.rtl  import NormalQueueRTL
from pclib.ifcs.SendRecvIfc import *

class ChannelUnitRTL( RTLComponent ):
  def construct(s, PacketType, QueueType=None, latency=2, num_entries=2):

    # Constant
    s.QueueType   = QueueType
    s.latency     = latency
    s.num_entries = num_entries

    # Interface
    s.recv  = RecvIfcRTL( PacketType )
    s.send  = SendIfcRTL( PacketType )

    if s.QueueType != None and s.latency != 0:
      # Component
      s.queues = [s.QueueType(s.num_entries, Type = PacketType) 
                   for _ in range (s.latency)]

      # Connections
      s.connect( s.recv.rdy, s.queues[0].enq.rdy )
#      s.connect( s.recv.en,  s.queues[0].enq.val )
#      s.connect( s.recv.msg, s.queues[0].enq.msg )

      @s.update
      def process():
        last = s.latency - 1
        for i in range(s.latency - 1):
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
    if s.QueueType != None and s.latency != 0:
      return "{}({}){}".format(s.recv.msg, s.latency, s.send.msg)
    else:
      return "{}(0){}".format( s.recv.msg, s.send.msg)

