#=========================================================================
# OutputUnitRTLSourceSink_test.py
#=========================================================================
# Test for OutputUnitRTL using Source and Sink
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Feb 28, 2019

import pytest

from pymtl3 import *
from pymtl3.stdlib.test.test_srcs    import TestSrcRTL
from pymtl3.stdlib.test.test_sinks   import TestSinkRTL
from pymtl3.stdlib.test              import TestVectorSimulator

from router.OutputUnitRTL     import OutputUnitRTL
from pymtl3.stdlib.rtl.queues import NormalQueueRTL

#-------------------------------------------------------------------------
# TestVectorSimulator test
#-------------------------------------------------------------------------

def run_tv_test( dut, test_vectors ):

  # Define input/output functions

  def tv_in( dut, tv ):
    dut.recv.en  = tv[0]
    dut.recv.msg = tv[2]
    dut.send.rdy = tv[3]

  def tv_out( dut, tv ):
    if tv[1] != '?': assert dut.recv.rdy == tv[1]
    if tv[4] != '?': assert dut.send.en  == tv[4]
    if tv[5] != '?': assert dut.send.msg == tv[5]

  # Run the test

  sim = TestVectorSimulator( dut, test_vectors, tv_in, tv_out )
  sim.run_test()

def test_pipe_Bits():

  B1  = mk_bits(1)
  B32 = mk_bits(32)

  test_vector_0 = [
    # recv.en recv.rdy recv.msg send.rdy send.en send.msg
    [  B1(0),  B1(0),  B32(123), B1(0),  B1(0),  B32(123) ],
    [  B1(1),  B1(1),  B32(345), B1(1),  B1(1),  B32(345) ],
    [  B1(0),  B1(0),  B32(567), B1(0),  B1(0),  B32(567) ],
  ]

  test_vector_1 = [
    # recv.en recv.rdy recv.msg send.rdy send.en send.msg
    [  B1(1),  B1(1),  B32(123), B1(0),  B1(0),    '?'    ],
    [  B1(1),  B1(1),  B32(345), B1(0),  B1(0),  B32(123) ],
    [  B1(0),  B1(0),  B32(567), B1(0),  B1(0),  B32(123) ],
    [  B1(0),  B1(0),  B32(567), B1(1),  B1(1),  B32(123) ],
    [  B1(0),  B1(1),  B32(567), B1(1),  B1(1),  B32(345) ],
    [  B1(1),  B1(1),  B32(567), B1(0),  B1(0),    '?'    ],
    [  B1(1),  B1(1),  B32(0  ), B1(1),  B1(1),  B32(567) ],
    [  B1(1),  B1(1),  B32(1  ), B1(1),  B1(1),  B32(0  ) ],
    [  B1(1),  B1(1),  B32(2  ), B1(1),  B1(1),  B32(1  ) ],
    [  B1(0),  B1(1),  B32(2  ), B1(1),  B1(1),  B32(2  ) ],
  ]
  run_tv_test( OutputUnitRTL( Bits32 ), test_vector_0)
#  run_tv_test( OutputUnitRTL( Bits32, NormalQueueRTL ), test_vector_1)

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, MsgType, src_msgs, sink_msgs, src_initial,
                 src_interval, sink_initial, sink_interval,
                 arrival_time=None ):

    s.src  = TestSrcRTL    ( MsgType, src_msgs,  src_initial,  src_interval  )
    s.sink = TestSinkRTL   ( MsgType, sink_msgs, sink_initial, sink_interval )
    s.dut  = OutputUnitRTL ( MsgType )

    # Connections
    s.connect( s.src.send, s.dut.recv  )
    s.connect( s.dut.send, s.sink.recv )
  
  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return s.src.line_trace() + "-> | " + s.dut.line_trace() + \
                               " | -> " + s.sink.line_trace()

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
# Test cases
#-------------------------------------------------------------------------

test_msgs = [ Bits16( 4 ), Bits16( 1 ), Bits16( 2 ), Bits16( 3 ) ]

arrival_pipe   = [ 2, 3, 4, 5 ]

def test_normal2_simple():
  th = TestHarness( Bits16, test_msgs, test_msgs, 0, 0, 0, 0,
                    arrival_pipe )
  run_sim( th )
