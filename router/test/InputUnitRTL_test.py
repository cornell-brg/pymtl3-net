#=========================================================================
#InputUnitRTLSourceSink_test.py
#=========================================================================
# Test for InputUnitRTL using Source and Sink
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Feb 23, 2019

import pytest

from pymtl import *
from pclib.rtl.valrdy_queues import PipeQueue1RTL, BypassQueue1RTL
from pclib.rtl.TestSource import TestSourceValRdy
from pclib.rtl.TestSink   import TestSinkValRdy
from pclib.ifcs import InValRdyIfc, OutValRdyIfc 
from pclib.ifcs.EnRdyIfc import InEnRdyIfc, OutEnRdyIfc
from pclib.test import mk_test_case_table
from pymtl.passes.PassGroups import SimpleSim

from router.InputUnitRTL import InputUnitRTL
from ocn_pclib.enrdy_adapters import ValRdy2EnRdy, EnRdy2ValRdy

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( RTLComponent ):

  def construct( s, num_msgs, MsgType, src_msgs, sink_msgs, stall_prob,
                 src_delay, sink_delay ):

    s.src      = TestSourceValRdy( MsgType, src_msgs  )
    s.vr_to_er = ValRdy2EnRdy    ( MsgType            )
    s.er_to_vr = EnRdy2ValRdy    ( MsgType            )
    s.sink     = TestSinkValRdy  ( MsgType, sink_msgs )
    s.input_unit   = InputUnitRTL    ( num_msgs, MsgType  )

    # Connections
    s.connect( s.src.out,      s.vr_to_er.in_ )
    s.connect( s.vr_to_er.out, s.input_unit.recv  )
    s.connect( s.input_unit.send,  s.er_to_vr.in_ )
    s.connect( s.er_to_vr.out, s.sink.in_     )
  
  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return s.src.line_trace() + "-> | " + s.input_unit.line_trace() + \
                               " | -> " + s.sink.line_trace()

#-------------------------------------------------------------------------
# run_rtl_sim
#-------------------------------------------------------------------------

def run_rtl_sim( test_harness, max_cycles=100 ):

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
  ]

#-------------------------------------------------------------------------
# directed tests
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  ( "         num_msgs   msg_func    stall src_delay sink_delay" ),
  [ "basic",      4,      basic_msgs, 0.0,  0,        0           ]
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

  return ( src_msgs, sink_msgs )

@pytest.mark.parametrize( **test_case_table )
def test( test_params ):
 
  msgs = test_params.msg_func()
  src_msgs, sink_msgs = mk_test_msgs( msgs )
  
  print ""
  run_rtl_sim( 
    TestHarness( test_params.num_msgs, Bits16, src_msgs, sink_msgs, test_params.stall, 
                 test_params.src_delay, test_params.sink_delay )
  )


