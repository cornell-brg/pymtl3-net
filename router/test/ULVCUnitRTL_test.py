#=========================================================================
# Tests for ULVCUnitGiveRTL 
#=========================================================================
#
# Author: Yanghui Ou
#   Date: Mar 24, 2019

import pytest

from pymtl                    import *
from pymtl.passes.PassGroups  import SimpleSim
from pclib.test.test_srcs     import TestSrcRTL
from pclib.test.test_sinks    import TestSinkRTL
from pclib.test               import TestVectorSimulator
from pclib.rtl.queues         import NormalQueueRTL
from router.InputUnitRTL      import InputUnitRTL 
from router.ULVCUnitRTL       import ULVCUnitRTL 
from ocn_pclib.ifcs.Packet    import *

#-------------------------------------------------------------------------
# TestVectorSimulator test
#-------------------------------------------------------------------------

def run_tv_test( dut, test_vectors ):

  # Define input/output functions

  def tv_in( dut, tv ):
    pkt = mk_pkt( 0, 0, 1, 1, tv[3], tv[2] )
    dut.recv.en  = tv[0]
    dut.recv.msg = pkt
    dut.give.en  = tv[4]

  def tv_out( dut, tv ):
    if tv[1] != '?': assert dut.recv.rdy == tv[1]
    if tv[5] != '?': assert dut.give.rdy == tv[5]
    if tv[6] != '?': assert dut.give.msg.payload == tv[6]

  # Run the test

  sim = TestVectorSimulator( dut, test_vectors, tv_in, tv_out )
  sim.run_test()

def test_pipe_Bits():

  B1  = mk_bits(1)
  B32 = mk_bits(32)
  dut = ULVCUnitRTL( Packet )
  dut.set_parameter("top.upper.elaborate.num_entries", 2)
  dut.set_parameter("top.lower.elaborate.num_entries", 2)
  run_tv_test( dut , [
    # recv.en recv.rdy recv.msg opaque give.en give.rdy give.msg
    [  B1(1),  B1(1),  B32(1), B1(0), B1(0),  B1(0),    '?'    ],
    [  B1(1),  B1(1),  B32(2), B1(1), B1(0),  B1(1),    '?'    ],
    [  B1(1),  B1(1),  B32(3), B1(0), B1(0),  B1(1),    '?'    ],
    [  B1(1),  B1(1),  B32(4), B1(1), B1(1),  B1(1),  B32( 1 ) ],
    [  B1(0),  B1(1),  B32(5), B1(0), B1(1),  B1(1),  B32( 2 ) ],
    [  B1(1),  B1(1),  B32(6), B1(1), B1(1),  B1(1),  B32( 3 ) ],
    [  B1(1),  B1(1),  B32(7), B1(0), B1(1),  B1(1),  B32( 4 ) ],
    [  B1(1),  B1(1),  B32(8), B1(1), B1(1),  B1(1),  B32( 7 ) ],
    [  B1(1),  B1(1),  B32(9), B1(0), B1(1),  B1(1),  B32( 6 ) ],
    [  B1(0),  B1(1),  B32(0), B1(1), B1(1),  B1(1),  B32( 9 ) ],
] )

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, MsgType, src_msgs, sink_msgs, src_initial,
                 src_interval, sink_initial, sink_interval,
                 arrival_time=None ):

    s.src  = TestSrcRTL   ( MsgType, src_msgs,  src_initial,  src_interval  )
    s.sink = TestSinkRTL  ( MsgType, sink_msgs, sink_initial, sink_interval )
    s.dut  = InputUnitRTL ( MsgType  )

    # Connections
    s.connect( s.src.send,     s.dut.recv  )
    s.connect( s.dut.give.msg, s.sink.recv.msg )

    @s.update
    def up_give_en():
      if s.dut.give.rdy and s.sink.recv.rdy:
        s.dut.give.en  = 1
        s.sink.recv.en = 1
      else:
        s.dut.give.en  = 0
        s.sink.recv.en = 0

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

  test_harness.set_parameter("top.dut.queue.elaborate.num_entries", 2)
  test_harness.set_parameter("top.dut.elaborate.QueueType", NormalQueueRTL)

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
  #run_sim( th )
