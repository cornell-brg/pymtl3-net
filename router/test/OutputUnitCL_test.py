#=========================================================================
# OutputUnitRTLSourceSink_test.py
#=========================================================================
# Test for OutputUnitRTL using Source and Sink
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Feb 28, 2019

import pytest

from pymtl3 import *
from pymtl3.stdlib.test.test_srcs  import TestSrcCL
from pymtl3.stdlib.test.test_sinks import TestSinkCL
from pymtl3.stdlib.cl.queues   import NormalQueueCL
from router.OutputUnitCL   import OutputUnitCL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, MsgType, src_msgs, sink_msgs, src_initial,
                 src_interval, sink_initial, sink_interval,
                 arrival_time=None ):

    s.src  = TestSrcCL   ( src_msgs,  src_initial,  src_interval  )
    s.sink = TestSinkCL  ( sink_msgs, sink_initial, sink_interval )
    s.dut  = OutputUnitCL( MsgType )

    # Connections
    s.connect( s.dut.send, s.sink.recv )
    s.connect( s.src.send, s.dut.recv  )
  
  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return "{} {} {}".format(
      s.src.line_trace(),
      s.dut.line_trace(),
      s.sink.line_trace(),
    )

#-------------------------------------------------------------------------
# run_rtl_sim
#-------------------------------------------------------------------------

def run_sim( test_harness, max_cycles=100 ):

  # Set parameters

#  test_harness.set_param("top.dut.queue.elaborate.num_entries", 4)
#  test_harness.set_param("top.dut.elaborate.QueueType", NormalQueueRTL)

  # Create a simulator

  test_harness.apply( SimpleSim )
  test_harness.sim_reset()


  # Run simulation

  ncycles = 0
  print ""
  print "{:2}:{}".format( ncycles, test_harness.line_trace() )
  while not test_harness.done() and ncycles < max_cycles:
    test_harness.tick()
    ncycles += 1
    print "{:2}:{}".format( ncycles, test_harness.line_trace() )

  # Check timeout

  assert ncycles < max_cycles

  test_harness.tick()
  test_harness.tick()
  test_harness.tick()

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

test_msgs = [ Bits16( 4 ), Bits16( 1 ), Bits16( 2 ), Bits16( 3 ) ]

def test_normal2_simple():
  th = TestHarness( Bits16, test_msgs, test_msgs, 0, 0, 0, 0 )
  run_sim( th )
