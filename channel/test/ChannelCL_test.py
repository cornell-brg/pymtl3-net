#=========================================================================
# ChannelCL_test.py
#=========================================================================
# Test for CL channel.
#
# Author : Yanghui Ou
#   Date : May 19, 2019

import pytest

from pymtl3 import *
from pymtl3.stdlib.test.test_srcs import TestSrcCL
from pymtl3.stdlib.test.test_sinks import TestSinkCL
from pymtl3.stdlib.cl.queues import NormalQueueCL

from ..ChannelCL import ChannelCL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, MsgType, src_msgs, sink_msgs ):

    s.src  = TestSrcCL ( MsgType, src_msgs  )
    s.sink = TestSinkCL( MsgType, sink_msgs )
    s.dut  = ChannelCL ( MsgType, latency=1 )

    # Connections
    s.src.send //= s.dut.recv
    s.dut.send //= s.sink.recv

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return s.src.line_trace() + "-> | " + s.dut.line_trace() + \
                               " | -> " + s.sink.line_trace()

#-------------------------------------------------------------------------
# run_rtl_sim
#-------------------------------------------------------------------------

def run_sim( test_harness, max_cycles=100 ):

  # Create a simulator

  test_harness.apply( DynamicSim )
  test_harness.sim_reset()


  # Run simulation

  ncycles = 0
  print()
  print( "{:2}:{}".format( ncycles, test_harness.line_trace() ))
  while not test_harness.done() and ncycles < max_cycles:
    test_harness.tick()
    ncycles += 1
    print( "{:2}:{}".format( ncycles, test_harness.line_trace() ))

  # Check timeout

  assert ncycles < max_cycles

  test_harness.tick()
  test_harness.tick()
  test_harness.tick()

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

test_msgs = [ b16(4), b16(1), b16(2), b16(3) ]

def test_chnl_simple():
  th = TestHarness( Bits16, test_msgs, test_msgs )
  run_sim( th )
