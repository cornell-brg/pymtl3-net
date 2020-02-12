'''
==========================================================================
test_srcs.py
==========================================================================
A collection of test sources.

Author : Yanghui Ou
  Date : Feb 2, 2020
'''
from collections import deque

from pymtl3 import *
from ..utils import get_nbits

#-------------------------------------------------------------------------
# MultiFlitPacketSourceCL
#-------------------------------------------------------------------------
# pkts                : a list of MultiFlitPacket objects.
# initial_delay       : number of cycles before sending the very first flit.
# flit_interval_delay : number of cycles between each flit in a packet.
# packet_interval_delay  : number of cycles between each packet.
# TODO: check if inputs packtes are valid

class MultiFlitPacketSourceCL( Component ):

  def construct( s, Format, pkts, initial_delay=0, flit_interval_delay=0, packet_interval_delay=0 ):

    # Interface
    PhitType = mk_bits( get_nbits( Format ) )
    s.send = NonBlockingCallerIfc( Type=PhitType )

    # Metadata
    s.pkts    = deque( pkts )
    s.cur_pkt = None
    s.count   = initial_delay
    s.f_delay = flit_interval_delay
    s.p_delay = packet_interval_delay

    # Update block
    @s.update
    def up_src_send():
      if s.count > 0:
        s.count -= 1
      elif not s.reset:
        # pop a packet to send
        if not s.cur_pkt and s.pkts:
          s.cur_pkt = s.pkts.popleft()
          assert not s.cur_pkt.empty()

        if s.send.rdy() and s.cur_pkt:
          s.send( s.cur_pkt.pop() )

          if s.cur_pkt.empty():
            s.cur_pkt = None
            s.count   = s.p_delay
          else:
            s.count   = s.f_delay

  def done( s ):
    return not s.pkts and not s.cur_pkt

  def line_trace( s ):
    return f'({s.count}){s.send}'
