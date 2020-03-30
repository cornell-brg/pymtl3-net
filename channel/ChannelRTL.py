#=========================================================================
# ChannelRTL.py
#=========================================================================
# CL channel module for connecting routers to form network. This simple
# channel has latency insensitive send/recv interfaces.
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 16, 2019

from ocnlib.ifcs.PhysicalDimension import PhysicalDimension
from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL
from pymtl3.stdlib.rtl.queues import NormalQueueRTL


class ChannelRTL( Component ):
  def construct(s, PacketType, QueueType=NormalQueueRTL, latency=0 ):

    # Constant
    s.dim = PhysicalDimension()
    s.QueueType   = QueueType
    s.latency     = latency
    s.num_entries = 2

    # Interface
    s.recv  = RecvIfcRTL( PacketType )
    s.send  = SendIfcRTL( PacketType )

    if s.QueueType != None and s.latency > 0:

      # Component

      s.queues = [ s.QueueType( PacketType, s.num_entries )
                   for _ in range( s.latency ) ]

      # Connections

      s.recv.rdy //= s.queues[0].enq.rdy

      s.queues[0].enq.msg //= s.recv.msg
      for i in range(s.latency-1):
        s.queues[i+1].enq.msg //= s.queues[i].deq.ret
      s.queues[-1].deq.ret //= s.send.msg

      @update
      def process():
        s.queues[0].enq.en @= s.recv.en & s.queues[0].enq.rdy
        for i in range(s.latency - 1):
          s.queues[i+1].enq.en @= s.queues[i].deq.rdy & s.queues[i+1].enq.rdy
          s.queues[i].deq.en   @= s.queues[i].deq.rdy & s.queues[i+1].enq.rdy

        s.send.en @= s.send.rdy & s.queues[s.latency-1].deq.rdy
        s.queues[s.latency-1].deq.en @= s.send.rdy & s.queues[s.latency-1].deq.rdy

    else:

      # If latency==0 simply bypass

      s.recv //= s.send

  def line_trace( s ):
    if s.QueueType != None and s.latency != 0:
      trace = '>'
      for i in range( s.latency ):
        trace += s.queues[i].line_trace() + '>'
      return f"{s.recv.msg}({trace}){s.send.msg}"
    else:
      return f"{s.recv}(0){s.send}"

  def elaborate_physical( s ):
    s.dim.w = 250
