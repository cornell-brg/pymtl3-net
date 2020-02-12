'''
==========================================================================
test_sinks.py
==========================================================================
A collection of test sinks.

Author : Yanghui Ou
  Date : Feb 3, 2020
'''
from pymtl3 import *
from ..utils import get_nbits
from ..packets import MultiFlitPacket as Packet

#-------------------------------------------------------------------------
# MultiFlitPacketSink
#-------------------------------------------------------------------------

class MultiFlitPacketSinkCL( Component ):

  def construct( s, Format, pkts, initial_delay=0, flit_interval_delay=0,
                 packet_interval_delay=0, cmp_fn=lambda a, b : a.flits == b.flits ):

    PhitType = mk_bits( get_nbits( Format ) )
    s.recv.Type = PhitType
    s.Format    = Format

    s.cur_pkt  = Packet( Format )
    s.ref_pkts = list( pkts )
    s.count    = initial_delay

    s.cmp_fn    = cmp_fn
    s.error_msg = ''

    s.all_received = False
    s.done_flag    = False
    s.recv_called  = False

    @s.update
    def up_sink_count():
      # Raise exception at the start of next cycle so that the errored
      # line trace gets printed out
      if s.error_msg:
        raise Exception( s.error_msg )

      # Tick one more cycle after message is received so that the
      # exception gets thrown
      if s.all_received:
        s.done_flag = True

      if len( s.ref_pkts ) == 0:
        s.all_received = True

      # If recv was called in previous cycle
      if s.recv_called:
        if s.cur_pkt.empty():
          s.count = packet_interval_delay
        else:
          s.count = flit_interval_delay

      elif s.count != 0:
        s.count -= 1

      else:
        s.count = 0

      s.recv_called = False

    # Constraints
    s.add_constraints(
      U( up_sink_count ) < M( s.recv     ),
      U( up_sink_count ) < M( s.recv.rdy ),
    )

  @non_blocking( lambda s: s.count==0 )
  def recv( s, flit ):
    assert s.count == 0
    s.recv_called = True

    # Received more packets
    if len( s.ref_pkts ) == 0:
      s.error_msg = (
        f'Test sink {s} received more flits than expected!\n'
        f'Received : {flit}'
      )

    # Assemble packet
    s.cur_pkt.add( flit )

    # If a packet is assembled, check if it exists in the reference
    if s.cur_pkt.full():

      # Check
      flag = False
      for i, pkt in enumerate( s.ref_pkts ):
        if s.cmp_fn( s.cur_pkt, pkt ):
          flag = True
          s.ref_pkts.pop( i )
          break

      if not flag:
        s.error_msg = (
          f'Test sink {s} received unexpected packet!\n'
          f'Received : {s.cur_pkt.flits}'
        )

      # Reset current packet to empty
      s.cur_pkt = Packet( s.Format )

  def done( s ):
    return s.done_flag

  def line_trace( s ):
    return f'{s.recv}({s.count})'

