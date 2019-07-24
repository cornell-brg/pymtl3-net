#=========================================================================
# net_sinks
#=========================================================================
# Test sinks for networks, which does not check the order of the received
# messages.
#
# Author : Yanghui Ou
#   Date : Apr 30, 2019

from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, RecvRTL2SendCL, enrdy_to_str

#-------------------------------------------------------------------------
# TestNetSinkCL
#-------------------------------------------------------------------------

class TestNetSinkCL( Component ):

  def construct( s,
    Type,
    msgs,
    initial_delay=0,
    interval_delay=0,
    arrival_time=None,
    match_func=lambda a, b : a.src == b.src and a.dst==b.dst and a.payload == b.payload,
  ):

    s.recv.Type = Type

    # [msgs] and [arrival_time] must have the same length.
    if arrival_time is not None:
      assert len( msgs ) == len( arrival_time )

    s.idx          = 0
    s.cycle_count  = 0
    s.msgs         = list( msgs )
    s.nmsgs        = len( msgs )
    s.arrival_time = None if arrival_time is None else \
                     list( arrival_time )
    s.perf_regr    = True if arrival_time is not None else False
    s.error_msg    = ""
    # TODO: maybe make this a parameter
    s.match_func   = match_func

    s.initial_count  = initial_delay
    s.interval_delay = interval_delay
    s.interval_count = 0

    s.recv_msg    = None
    s.recv_called = False
    s.recv_rdy    = False
    s.trace_len   = len( str( s.msgs[0] ) ) if len(s.msgs) != 0 else 0
#    s.trace_len   = len( str( s.msgs[0] ) )

    @s.update
    def up_sink_count():
      if s.error_msg:
        raise Exception( s.error_msg )
      if not s.reset:
        s.cycle_count += 1
      else:
        s.cycle_count = 0

      # if recv was called in previous cycle
      if s.recv_called:
        s.interval_count = s.interval_delay

      elif s.initial_count != 0:
        s.initial_count -= 1

      elif s.interval_count != 0:
        s.interval_count -= 1

      else:
        s.interval_count = 0

      s.recv_called = False
      s.recv_msg    = None
      s.recv_rdy    = s.initial_count == 0 and s.interval_count == 0

    s.add_constraints(
      U( up_sink_count ) < M( s.recv ),
      U( up_sink_count ) < M( s.recv.rdy )
    )

  @non_blocking( lambda s: s.initial_count==0 and s.interval_count==0 )
  def recv( s, msg ):

    s.recv_msg = msg

    # Sanity check
    if s.idx >= s.nmsgs:
      s.error_msg = ("""
Test Sink received more msgs than expected
Received : {}
""".format( msg ) )

    # Check correctness first
    if not [ pkt for pkt in s.msgs if s.match_func( s.recv_msg, pkt) ]:
      # FIXME: s.idx does not mean anything here...
      s.error_msg = ("""
Test Sink {} received WRONG msg!
Received : {}
""".format( str(s), s.recv_msg ) )

    # Check performace regression
    elif s.perf_regr and s.cycle_count > s.arrival_time[ s.idx ]:
      s.error_msg = ("""
Test Sink {} received msg LATER than expected!
Message        : {}
Expected cycles: {}
Received at    : {}""".format( str(s), s.msgs[ s.idx ], s.arrival_time[ s.idx ], s.cycle_count ) )

    # No error
    else:
      s.idx += 1
      s.recv_called = True
      # Remove received pkt from list
      for pkt in s.msgs:
        if s.match_func( s.recv_msg, pkt ):
          s.msgs.remove( pkt )
          break

  def done( s ):
    return s.idx >= s.nmsgs

  # Line trace
  def line_trace( s ):
    return "{}".format( s.recv )

#-------------------------------------------------------------------------
# TestSinkRTL
#-------------------------------------------------------------------------

class TestNetSinkRTL( Component ):

  def construct( s,
    MsgType,
    msgs,
    initial_delay=0,
    interval_delay=0,
    arrival_time=None,
    match_func=lambda a, b : a.src == b.src and a.dst==b.dst and a.payload == b.payload,
  ):

    # Interface

    s.recv = RecvIfcRTL( MsgType )

    # Components

    s.sink    = TestNetSinkCL( MsgType, msgs, initial_delay, interval_delay,
                               arrival_time, match_func )
    s.adapter = RecvRTL2SendCL( MsgType )

    s.recv         //= s.adapter.recv
    s.adapter.send //= s.sink.recv

  def done( s ):
    return s.sink.done()

  # Line trace

  def line_trace( s ):
    return "{}".format( s.recv )
