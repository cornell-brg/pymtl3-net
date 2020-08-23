'''
==========================================================================
DummyCore.py
==========================================================================
A dummy core that streams data into the network.

Author: Yanghui Ou
  Date: Jun 21, 2020
'''

from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL
from .queues import NormalQueueRTL

class DummyCore( Component ):

  def construct( s, Header ):

    # Local parameter

    s.PhitType = mk_bits( Header.nbits )

    # Interface

    # interfaces that connects to the chip edge
    s.send = SendIfcRTL( s.PhitType )
    s.recv = RecvIfcRTL( s.PhitType )

    # Component

    s.in_q  = NormalQueueRTL( s.PhitType, num_entries=1 )
    s.out_q = NormalQueueRTL( s.PhitType, num_entries=1 )

    # Connect and logic

    s.recv         //= s.in_q.enq

    s.in_q.deq.ret //= s.out_q.enq.msg
    s.in_q.deq.en  //= lambda: s.out_q.enq.rdy & s.in_q.deq.rdy
    s.out_q.enq.en //= lambda: s.out_q.enq.rdy & s.in_q.deq.rdy

    s.send.msg     //= s.out_q.deq.ret
    s.send.en      //= lambda: s.out_q.deq.rdy & s.send.rdy
    s.out_q.deq.en //= lambda: s.out_q.deq.rdy & s.send.rdy

  def line_trace( s ):
    return f'{s.recv}(){s.send}'

# class DummyCore( Component ):
#
#   def construct( s, Header ):
#
#     # Local parameter
#
#     s.PhitType = mk_bits( Header.nbits )
#
#     # Interface
#
#     # interfaces that connects to the chip edge
#     s.send = SendIfcRTL( s.PhitType )
#     s.recv = RecvIfcRTL( s.PhitType )
#
#     # interfaces that connects to the network
#     s.net_send = SendIfcRTL( s.PhitType )
#     s.net_recv = RecvIfcRTL( s.PhitType )
#
#     # Component
#
#     s.in_q  = NormalQueueRTL( s.PhitType )
#     s.out_q = NormalQueueRTL( s.PhitType )
#
#     # Connect and logic
#
#     s.recv         //= s.in_q.enq
#     s.send.msg     //= s.out_q.deq.ret
#     s.send.en      //= lambda: s.out_q.deq.rdy & s.send.rdy
#     s.out_q.deq.en //= lambda: s.out_q.deq.rdy & s.send.rdy
#
#     s.net_recv     //= s.out_q.enq
#     s.net_send.msg //= s.in_q.deq.ret
#     s.net_send.en  //= lambda: s.in_q.deq.rdy & s.net_send.rdy
#     s.in_q.deq.en  //= lambda: s.in_q.deq.rdy & s.net_send.rdy
#
#   def line_trace( s ):
#     return f'{s.recv},{s.send}(){s.net_recv},{s.net_send}'

