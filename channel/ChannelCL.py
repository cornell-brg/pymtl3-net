#=========================================================================
# ChannelCL.py
#=========================================================================
# CL channel module for connecting routers to form network. This simple
# channel has latency insensitive send/recv interfaces.
#
# Author : Yanghui Ou
#   Date : May 19, 2019

from pymtl3 import *
from pymtl3.stdlib.cl.queues import NormalQueueCL


class ChannelCL( Component ):

  def construct( s, PacketType, QueueType = NormalQueueCL, latency = 0 ):

    # Interface

    s.recv = CalleeIfcCL()
    s.send = CallerIfcCL()
    s.QueueType = QueueType

    # Constants

    s.latency = latency
    assert s.latency >= 0

    # Channel queue placement

    if s.latency == 0:

      s.recv //= s.send

    else:

      s.queues = [ QueueType( num_entries=2 ) for i in range( s.latency ) ]

      s.recv //= s.queues[0].enq

      @update
      def chnl_up_send():

        for i in range( s.latency-1 ):
          if s.queues[i].deq.rdy() and s.queues[i+1].enq.rdy():
            s.queues[i+1].enq( s.queues[i].deq() )

        if s.queues[-1].deq.rdy() and s.send.rdy():
          s.send( s.queues[-1].deq() )

  def line_trace( s ):
    return f"{s.recv}(){s.send}"
