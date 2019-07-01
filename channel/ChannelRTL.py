#=========================================================================
# ChannelRTL.py
#=========================================================================
# A Link unit for connecting routers to form network.
#
# Author : Cheng Tan
#   Date : Mar 16, 2019

from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL
from pymtl3.stdlib.rtl.queues import NormalQueueRTL
from ocn_pclib.ifcs.PhysicalDimension import PhysicalDimension

class ChannelRTL( Component ):
  def construct(s, PacketType, QueueType=None, latency=2, num_entries=2):

    # Constant
    s.dim = PhysicalDimension()
    s.QueueType   = QueueType
    s.latency     = latency
    s.num_entries = num_entries

    # Interface
    s.recv  = RecvIfcRTL( PacketType )
    s.send  = SendIfcRTL( PacketType )

    if s.QueueType != None and s.latency != 0:
      # Component
      s.queues = [ s.QueueType( PacketType, s.num_entries ) 
                   for _ in range( s.latency ) ]

      # Connections
      s.connect( s.recv.rdy, s.queues[0].enq.rdy )

      @s.update
      def process():
        last = s.latency - 1
        s.queues[0].enq.msg = s.recv.msg
        s.queues[0].enq.en = s.recv.en and s.queues[0].enq.rdy
        for i in range(s.latency - 1):
          s.queues[i+1].enq.msg = s.queues[i].deq.msg
          s.queues[i+1].enq.en  = s.queues[i].deq.rdy and s.queues[i+1].enq.rdy
          s.queues[i].deq.en    = s.queues[i+1].enq.en

        s.send.msg  = s.queues[last].deq.msg
        s.send.en   = s.send.rdy and s.queues[last].deq.rdy
        s.queues[last].deq.en   = s.send.en

    else:
      s.connect(s.recv, s.send)

  def line_trace( s ):
    if s.QueueType != None and s.latency != 0:
      trace = '>'
      for i in range( s.latency ):
        trace += s.queues[i].line_trace() + '>'
      return "{}({}){}".format(s.recv.msg, trace, s.send.msg)
    else:
      return "{}(0){}".format( s.recv.msg, s.send.msg)

  def elaborate_physical( s ):
    s.dim.w = 100
