#=========================================================================
# Test sinks 
#=========================================================================
# Test sinks with CL and RTL interfaces.
#
# Author : Yanghui Ou
#   Date : Mar 11, 2019

from pymtl import *
from pymtl.dsl.ComponentLevel6 import method_port, ComponentLevel6
from pclib.ifcs                import RecvIfcRTL
from ocn_pclib.adapters        import RecvCL2SendRTL, RecvRTL2SendCL

#-------------------------------------------------------------------------
# TestSinkCL
#-------------------------------------------------------------------------

class TestSinkCL( ComponentLevel6 ):
  
  def construct( s, msgs, initial_delay=0, interval_delay=0 ):
    
    s.idx  = 0
    s.msgs = list( msgs )
    
    s.initial_cnt    = initial_delay
    s.interval_delay = interval_delay
    s.interval_cnt   = 0

    s.recv_msg    = None 
    s.recv_called = False 
    s.trace_len   = len( str( s.msgs[0] ) )

    @s.update
    def decr_cnt():

      # if recv was called in previous cycle
      if s.recv_called:
        s.interval_cnt = s.interval_delay

      s.recv_called = False
      s.recv_msg    = None

      if s.initial_cnt != 0:
        s.initial_cnt -= 1
      elif s.interval_cnt != 0:
        s.interval_cnt -= 1
      else:
        s.interval_cnt = 0

    s.add_constraints( U( decr_cnt ) < M( s.recv ) )
 
  @method_port( lambda s: s.recv_rdy() )
  def recv( s, msg ):

    s.recv_called = True
    s.recv_msg = msg
    # Sanity check 
    if s.idx >= len( s.msgs ):
      raise Exception( "Test Sink received more msgs than expected" )

    if s.recv_msg != s.msgs[s.idx]:
      raise Exception( """
        Test Sink received WRONG msg!
        Expected : {}
        Received : {}
        """.format( s.msgs[s.idx], s.recv_msg ) )
    else:
      s.idx += 1

  def recv_rdy( s ):
    return s.initial_cnt == 0 and s.interval_cnt==0

  def done( s ):
    return s.idx >= len( s.msgs )
  
  def line_trace( s ):
    trace = "." if not s.recv_called and s.recv.rdy() else \
            "#" if not s.recv_called and not s.recv.rdy() else \
            "X" if s.recv_called and not s.recv.rdy() else \
            str( s.recv_msg )

    return "{}".format( trace.ljust( s.trace_len ) )

#-------------------------------------------------------------------------
# TestSinkRTL
#-------------------------------------------------------------------------

class TestSinkRTL( ComponentLevel6 ):

  def construct( s, MsgType, msgs, initial_delay=0, interval_delay=0 ):

    # Interface

    s.recv = RecvIfcRTL( MsgType )

    # Components

    s.sink    = TestSinkCL( msgs, initial_delay, interval_delay )
    s.adapter = RecvRTL2SendCL( MsgType )
    
    s.connect( s.recv,         s.adapter.recv )
    s.connect( s.adapter.send, s.sink.recv    )

  def done( s ):
    return s.sink.done()

  # Line trace

  def line_trace( s ):
    return s.sink.line_trace()