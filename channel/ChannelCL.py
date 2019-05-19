#=========================================================================
# ChannelRTL.py
#=========================================================================
# A Link unit for connecting routers to form network.
#
# Author : Yanghui Ou
#   Date : May 19, 2019

from pymtl import *
from pclib.cl.queues import NormalQueueCL
from pclib.ifcs.GuardedIfc import (
  GuardedCallerIfc, 
  GuardedCalleeIfc, 
  guarded_ifc
)

class ChannelCL( Component ):

  def construct( s,
                 PacketType, 
                 QueueType = NormalQueueCL,
                 latency = 0 ):

    # Interface

    s.recv = GuardedCalleeIfc()
    s.send = GuardedCallerIfc()
    s.QueueType = QueueType
    
    # Constants

    s.latency = latency
    assert s.latency >= 0

    # Channel queue placement

    if s.latency == 0:
      s.connect( s.recv, s.send )

    else:
      s.queues = [ QueueType( size=2 ) for i in range( s.latency ) ]
      
      s.connect( s.recv, s.queues[0].enq )

      @s.update
      def chnl_up_send():

        for i in range( s.latency-1 ):
          if s.queues[i].deq.rdy() and s.queues[i+1].enq.rdy():
            s.queues[i+1].enq( s.queues[i].deq() )
        if s.queues[-1].deq.rdy() and s.send.rdy():
          s.send( s.queues[-1].deq() )

  def line_trace( s ):
    return ""
