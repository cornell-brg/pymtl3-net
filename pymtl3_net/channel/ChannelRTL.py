#=========================================================================
# ChannelRTL.py
#=========================================================================
# CL channel module for connecting routers to form network. This simple
# channel has latency insensitive send/recv interfaces.
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 16, 2019

from pymtl3_net.ocnlib.ifcs.PhysicalDimension import PhysicalDimension
from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import RecvIfcRTL, SendIfcRTL
from pymtl3.stdlib.stream.queues import NormalQueueRTL


class ChannelRTL( Component ):
  def construct(s, PacketType, QueueType=NormalQueueRTL, latency=0 ):

    # Constant
    s.dim         = PhysicalDimension()
    s.QueueType   = QueueType
    s.latency     = latency
    s.num_entries = 2

    # Interface
    s.recv  = RecvIfcRTL( PacketType )
    s.send  = SendIfcRTL( PacketType )

    #---------------------------------------------------------------------
    # If latency > 0 and channel queue exists
    #---------------------------------------------------------------------

    if s.QueueType != None and s.latency > 0:

      # Component

      s.queues = [ s.QueueType( PacketType, s.num_entries )
                   for _ in range( s.latency ) ]

      # Connections

      s.recv //= s.queues[0].recv

      for i in range(s.latency-1):
        s.queues[i+1].recv //= s.queues[i].send
      s.queues[-1].send //= s.send

    #---------------------------------------------------------------------
    # If latency==0 simply bypass
    #---------------------------------------------------------------------

    else:

      s.recv //= s.send

  def line_trace( s ):
    if s.QueueType != None and s.latency != 0:
      trace = '>'
      for i in range( s.latency ):
        trace += s.queues[i].line_trace() + '>'
      return f"{s.recv}({trace}){s.send}"
    else:
      return f"{s.recv}(0){s.send}"

  def elaborate_physical( s ):
    s.dim.w = 250
