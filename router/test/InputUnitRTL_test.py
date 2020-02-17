"""
==========================================================================
InputUnitRTL_test.py
==========================================================================
Test cases for InputUnitRTL.

Author: Yanghui Ou
  Date: Mar 24, 2019
"""
import pytest

from pymtl3 import *
from pymtl3.stdlib.rtl.queues import (BypassQueueRTL, NormalQueueRTL,
                                      PipeQueueRTL)
from pymtl3.stdlib.test import TestVectorSimulator
from pymtl3.stdlib.test.test_sinks import TestSinkRTL
from pymtl3.stdlib.test.test_srcs import TestSrcRTL
from router.InputUnitRTL import InputUnitRTL

from .InputUnitCL_test import InputUnitCL_Tests as BaseTests

#-------------------------------------------------------------------------
# TestVectorSimulator test
#-------------------------------------------------------------------------

def run_tv_test( dut, test_vectors ):

  # Define input/output functions

  def tv_in( dut, tv ):
    dut.recv.en  = tv[0]
    dut.recv.msg = tv[2]
    dut.give.en  = tv[3]

  def tv_out( dut, tv ):
    if tv[1] != '?': assert dut.recv.rdy == tv[1]
    if tv[4] != '?': assert dut.give.rdy == tv[4]
    if tv[5] != '?': assert dut.give.ret == tv[5]

  # Run the test

  sim = TestVectorSimulator( dut, test_vectors, tv_in, tv_out )
  sim.run_test()

def test_pipe_Bits():

  run_tv_test( InputUnitRTL( Bits32 ), [
    #  enq.en  enq.rdy enq.msg   deq.en  deq.rdy deq.msg
    [  b1(1),  b1(1),  b32(123), b1(0),  b1(0),    '?'    ],
    [  b1(1),  b1(1),  b32(345), b1(0),  b1(1),  b32(123) ],
    [  b1(0),  b1(0),  b32(567), b1(0),  b1(1),  b32(123) ],
    [  b1(0),  b1(0),  b32(567), b1(1),  b1(1),  b32(123) ],
    [  b1(0),  b1(1),  b32(567), b1(1),  b1(1),  b32(345) ],
    [  b1(1),  b1(1),  b32(567), b1(0),  b1(0),    '?'    ],
    [  b1(1),  b1(1),  b32(0  ), b1(1),  b1(1),  b32(567) ],
    [  b1(1),  b1(1),  b32(1  ), b1(1),  b1(1),  b32(0  ) ],
    [  b1(1),  b1(1),  b32(2  ), b1(1),  b1(1),  b32(1  ) ],
    [  b1(0),  b1(1),  b32(2  ), b1(1),  b1(1),  b32(2  ) ],
] )

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, MsgType, src_msgs, sink_msgs ):

    s.src  = TestSrcRTL   ( MsgType, src_msgs )
    s.dut  = InputUnitRTL ( MsgType )
    s.sink = TestSinkRTL  ( MsgType, sink_msgs )

    # Connections
    s.src.send     //= s.dut.recv
    s.dut.give.ret //= s.sink.recv.msg

    @s.update
    def up_give_en():
      if s.dut.give.rdy and s.sink.recv.rdy:
        s.dut.give.en  = b1(1)
        s.sink.recv.en = b1(1)
      else:
        s.dut.give.en  = b1(0)
        s.sink.recv.en = b1(0)

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


class InputUnitRTL_Tests( BaseTests ):

  @classmethod
  def setup_class( cls ):
    cls.TestHarness = TestHarness
    cls.qtypes      = [ NormalQueueRTL, BypassQueueRTL, PipeQueueRTL ]
