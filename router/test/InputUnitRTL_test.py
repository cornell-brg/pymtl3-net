#=========================================================================
# InputUnitRTLSourceSink_test.py
#=========================================================================
# Test for InputUnitRTL using Source and Sink
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Feb 23, 2019

import pytest

from pymtl import *
from pclib.rtl.valrdy_queues import PipeQueue1RTL, BypassQueue1RTL
from pclib.rtl.TestSource import TestSourceEnRdy
from pclib.rtl.TestSink   import TestSinkEnRdy
from pclib.ifcs import InValRdyIfc, OutValRdyIfc 
from pclib.ifcs.SendRecvIfc import *
from pclib.test import mk_test_case_table
from pymtl.passes.PassGroups import SimpleSim

from router.InputUnitRTL import InputUnitRTL

from pclib.rtl  import NormalQueueRTL
from pclib.rtl  import BypassQueue1RTL

from ocn_pclib.ifcs.Packet import *

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( RTLComponent ):

  def construct( s, MsgType, src_msgs, sink_msgs, stall_prob,
                 src_delay, sink_delay ):

    s.src      = TestSourceEnRdy( MsgType, src_msgs  )
    s.sink     = TestSinkEnRdy  ( MsgType, sink_msgs )
    s.input_unit   = InputUnitRTL    ( MsgType  )

    # Connections
    s.connect( s.src.out,             s.input_unit.recv)
    s.connect( s.input_unit.send, s.sink.in_ )
  
  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return s.src.line_trace() + "-> | " + s.input_unit.line_trace() + \
                               " | -> " + s.sink.line_trace()

#-------------------------------------------------------------------------
# run_rtl_sim
#-------------------------------------------------------------------------

def run_rtl_sim( test_harness, max_cycles=100 ):

  # Set parameters

#  test_harness.set_parameter("top.input_unit.queue.elaborate.num_entries", 4)
  test_harness.set_parameter("top.input_unit.elaborate.QueueType", NormalQueueRTL)

  # Create a simulator

  test_harness.apply( SimpleSim )


  # Run simulation

  ncycles = 0
  print ""
  print "{}:{}".format( ncycles, test_harness.line_trace() )
  while not test_harness.done() and ncycles < max_cycles:
    test_harness.tick()
    ncycles += 1
    print "{}:{}".format( ncycles, test_harness.line_trace() )

  # Check timeout

  assert ncycles < max_cycles

  test_harness.tick()
  test_harness.tick()
  test_harness.tick()

#-------------------------------------------------------------------------
# directed tests
#-------------------------------------------------------------------------

def basic_msgs():
  return [
    # src, sink
    [ Bits16( 0  ),  Bits16( 0  )  ],
    [ Bits16( 4  ),  Bits16( 4  )  ],
    [ Bits16( 9  ),  Bits16( 9  )  ],
    [ Bits16( 11 ),  Bits16( 11 )  ],
    [ Bits16( 15 ),  Bits16( 15 )  ],
  ]

#-------------------------------------------------------------------------
# directed tests
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  ( "          msg_func    stall src_delay sink_delay" ),
  [ "basic",  basic_msgs,   0.0,     0,        0        ]
])

#-------------------------------------------------------------------------
# mk_test_msgs
#-------------------------------------------------------------------------

def mk_test_msgs( msg_list ):

  src_msgs  = []
  sink_msgs = []

  for m in msg_list:
    src_msgs.append ( m[0] )
    sink_msgs.append( m[1] )
#    src_msgs.append(  mk_pkt(m[0], m[0], m[0], m[0], m[0], Bits16( 9 )))
#    sink_msgs.append( mk_pkt(m[1], m[1], m[1], m[1], m[1], Bits16( 9 )))
#  print src_msgs[0].src_x
#  print src_msgs[1].src_x
#  print src_msgs[2].src_x

  return ( src_msgs, sink_msgs )

@pytest.mark.parametrize( **test_case_table )
def test( test_params ):
 
  msgs = test_params.msg_func()
  src_msgs, sink_msgs = mk_test_msgs( msgs )
  
  print ""
  run_rtl_sim( 
#    TestHarness( Packet, src_msgs, sink_msgs, test_params.stall, 
    TestHarness( Bits16, src_msgs, sink_msgs, test_params.stall, 
                 test_params.src_delay, test_params.sink_delay )
  )


