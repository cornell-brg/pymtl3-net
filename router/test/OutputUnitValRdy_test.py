"""
==========================================================================
OutputUnitValRdy_test.py
==========================================================================
Test cases for OutputUnitValRdy.

Author : Yanghui Ou
  Date : Oct 5, 2020
"""
import pytest

from pymtl3 import *

from pymtl3.stdlib.test_utils.test_sinks import TestSinkRTL
from pymtl3.stdlib.test_utils.test_srcs import TestSrcRTL

from ocnlib.ifcs.enrdy_adapters import InValRdy2Send, Recv2OutValRdy
from ocnlib.rtl.valrdy_queues import NormalQueueRTL

from .OutputUnitCL_test import OutputUnitCL_Tests as BaseTests
from ..OutputUnitValRdy import OutputUnitValRdy

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, MsgType, src_msgs, sink_msgs ):

    s.src   = TestSrcRTL( MsgType, src_msgs )
    s.dut   = OutputUnitValRdy( MsgType )
    s.sink  = TestSinkRTL( MsgType, sink_msgs )

    s.recv2out = Recv2OutValRdy( MsgType )
    s.in2send  = InValRdy2Send ( MsgType )

    # Connections

    s.src.send     //= s.recv2out.recv
    s.recv2out.out //= s.dut.in_
    s.dut.out      //= s.in2send.in_
    s.in2send.send //= s.sink.recv

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


class OutputUnitValRdy_Tests( BaseTests ):

  @classmethod
  def setup_class( cls ):
    cls.TestHarness = TestHarness
    cls.qtypes      = [ NormalQueueRTL ]
