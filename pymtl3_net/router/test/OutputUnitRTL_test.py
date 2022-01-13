"""
==========================================================================
OutputUnitRTL_test.py
==========================================================================
Test cases for OutputUnitRTL.

Author : Yanghui Ou, Cheng Tan
  Date : June 22, 2019
"""
import pytest

from pymtl3 import *
from pymtl3.stdlib.queues import (BypassQueueRTL, NormalQueueRTL,
                                      PipeQueueRTL)
from pymtl3.stdlib.test_utils.test_sinks import TestSinkCL
from pymtl3.stdlib.test_utils.test_srcs import TestSrcCL

from pymtl3_net.router.OutputUnitRTL import OutputUnitRTL

from .OutputUnitCL_test import OutputUnitCL_Tests as BaseTests

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, MsgType, src_msgs, sink_msgs ):

    s.src   = TestSrcCL( MsgType, src_msgs )
    s.src_q = BypassQueueRTL( MsgType, num_entries=1 )
    s.dut   = OutputUnitRTL( MsgType )
    s.sink  = TestSinkCL( MsgType, sink_msgs )

    # Connections
    s.src.send  //= s.src_q.enq
    s.src_q.deq //= s.dut.get
    s.dut.send  //= s.sink.recv

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return "{}>{}>{}".format(
      s.src.line_trace(),
      s.dut.line_trace(),
      s.sink.line_trace()
    )

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------


class OutputUnitRTL_Tests( BaseTests ):

  @classmethod
  def setup_class( cls ):
    cls.TestHarness = TestHarness
    cls.qtypes      = [ NormalQueueRTL, PipeQueueRTL, BypassQueueRTL ]
