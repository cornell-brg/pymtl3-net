#=========================================================================
# Tests for SwitchUnitCL 
#=========================================================================
#
# Author: Cheng Tan
#   Date: June 29, 2019

import pytest
from pymtl3                        import *
from pymtl3.passes.PassGroups      import SimpleSim
from pymtl3.stdlib.test.test_srcs  import TestSrcCL
from pymtl3.stdlib.test.test_sinks import TestSinkCL
from router.InputUnitCL            import InputUnitCL 
from router.SwitchUnitCL           import SwitchUnitCL 

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, MsgType, src_msgs, sink_msgs, src_initial,
                 src_interval, sink_initial, sink_interval,
                 arrival_time=None ):

    s.src  = [ TestSrcCL  ( MsgType, src_msgs[i],  src_initial,  src_interval  )
               for i in range( 5 ) ]
    s.sink = TestSinkCL ( MsgType, sink_msgs, sink_initial, sink_interval )
    s.dut  = SwitchUnitCL( MsgType )

    # Connections
    for i in range( 5 ):
      s.connect( s.src[i].send.rdy, s.dut.get[i].rdy )
    s.connect( s.dut.send, s.sink.recv )

#    @s.update
#    def up_ge_en():
#      for i in range( 5 ):
#        if s.dut_input[i].give.rdy() and s.sink.recv.rdy():
#          s.sink.recv( s.dut_input[i].give() )

  def done( s ):
    srcs_done = 1
    for i in range( 5 ):
      if s.srcs[i].done() == 0:
        srcs_done = 0
    return srcs_done and s.sink.done()

  def line_trace( s ):
    return "{} {} {}".format( 
      s.src.line_trace(), 
      s.dut_input.line_trace(), 
      s.dut_switch.line_trace(), 
      s.sink.line_trace(),
    )

#-------------------------------------------------------------------------
# run_rtl_sim
#-------------------------------------------------------------------------

def run_sim( test_harness, max_cycles=100 ):

  # Set parameters

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

test_msgs = [
             [],
             [Bits16( 4 ),Bits16( 1 )],
             [],
             [],
             [Bits16( 2 ),Bits16( 3 )]
            ]

arrival_pipe   = [ 2, 3, 4, 5 ]

def test_normal2_simple():
  th = TestHarness( Bits16, test_msgs, test_msgs, 0, 0, 0, 0,
                    arrival_pipe )
  run_sim( th )
