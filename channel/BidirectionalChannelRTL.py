'''
==========================================================================
BidirectionalChannelRTL.py
==========================================================================
Bi-directional channels that is composed of two uni-directional channel.

Author: Yanghui Ou
  Date: July 28, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL
from pymtl3.stdlib.queues import NormalQueueRTL

from .ChannelRTL import ChannelRTL

class BidirectionalChannelRTL( Component ):

  def construct( s, PacketType, QueueType=NormalQueueRTL, latency=0 ):

    # Interface

    s.recv = [ RecvIfcRTL( PacketType ) for _ in range(2) ]
    s.send = [ SendIfcRTL( PacketType ) for _ in range(2) ]

    s.chnls = [ ChannelRTL( PacketType, QueueType, latency ) for _ in range(2) ]

    for i in range(2):
      s.recv[i] //= s.chnls[i].recv
      s.send[i] //= s.chnls[i].send

  def line_trace( s ):
    return f'{s.recv[0]}|{s.recv[1]}(){s.send[0]}{s.send[1]}'
