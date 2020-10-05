"""
==========================================================================
InputUnitValRdy_test.py
==========================================================================
Test cases for InputUnitValRdy.

Author: Yanghui Ou
  Date: Oct 5, 2020
"""
import pytest

from pymtl3 import *
from pymtl3.stdlib.test_utils import TestVectorSimulator
from pymtl3.stdlib.test_utils.test_sinks import TestSinkRTL
from pymtl3.stdlib.test_utils.test_srcs import TestSrcRTL

from ocnlib.ifcs.enrdy_adapters import InValRdy2Send, Recv2OutValRdy
from ocnlib.rtl.valrdy_queues import NormalQueueRTL

from .InputUnitCL_test import InputUnitCL_Tests as BaseTests
from ..InputUnitValRdy import InputUnitValRdy

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, MsgType, src_msgs, sink_msgs ):

    s.src  = TestSrcRTL   ( MsgType, src_msgs )
    s.dut  = InputUnitValRdy ( MsgType )
    s.sink = TestSinkRTL  ( MsgType, sink_msgs )

    s.recv2out = Recv2OutValRdy( MsgType )
    s.in2send  = InValRdy2Send ( MsgType )

    s.src.send     //= s.recv2out.recv
    s.recv2out.out //= s.dut.in_
    s.dut.out      //= s.in2send.in_
    s.in2send.send //= s.sink.recv

    # # Connections
    # s.src.send     //= s.dut.recv
    # s.dut.give.ret //= s.sink.recv.msg



    # @update
    # def up_give_en():
    #   both_rdy = s.dut.give.rdy & s.sink.recv.rdy
    #   s.dut.give.en  @= both_rdy
    #   s.sink.recv.en @= both_rdy

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return "{} >>> {} >>> {}".format(
      s.src.line_trace(),
      s.dut.line_trace(),
      s.sink.line_trace(),
    )

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------


class InputUnitValRdy_Tests( BaseTests ):

  @classmethod
  def setup_class( cls ):
    cls.TestHarness = TestHarness
    cls.qtypes      = [ NormalQueueRTL ]
