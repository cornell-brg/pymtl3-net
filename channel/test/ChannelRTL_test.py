#=========================================================================
# InputUnitRTLSourceSink_test.py
#=========================================================================
# Test for InputUnitRTL using Source and Sink
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Feb 23, 2019

import pytest

from channel.ChannelRTL import ChannelRTL
from ocnlib.utils import run_sim
from pymtl3 import *
from pymtl3.stdlib.queues import NormalQueueRTL
from pymtl3.stdlib.test_utils import TestVectorSimulator
from pymtl3.stdlib.test_utils.test_sinks import TestSinkRTL
from pymtl3.stdlib.test_utils.test_srcs import TestSrcRTL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, MsgType, src_msgs, sink_msgs ):

    s.src  = TestSrcRTL ( MsgType, src_msgs  )
    s.sink = TestSinkRTL( MsgType, sink_msgs )
    s.dut  = ChannelRTL( MsgType )

    # Connections
    s.src.send //= s.dut.recv
    s.dut.send //= s.sink.recv

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return s.src.line_trace() + "-> | " + s.dut.line_trace() + \
                               " | -> " + s.sink.line_trace()

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

test_msgs = [ b16(4), b16(1), b16(2), b16(3) ]

def test_passthrough():
  th = TestHarness( Bits16, test_msgs, test_msgs)
  run_sim( th )

def test_normal2_simple():
  th = TestHarness( Bits16, test_msgs, test_msgs)
  th.set_param("top.dut.construct", latency=2)
  run_sim( th )

