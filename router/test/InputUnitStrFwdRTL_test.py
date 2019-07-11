"""
==========================================================================
InputUnitStrFwdRTL_test.py
==========================================================================
Test cases for InputUnitStrFwdRTL.

Author: Cheng Tan, Yanghui Ou
  Date: July 11, 2019
"""
import pytest

from pymtl3 import *
from pymtl3.stdlib.test.test_srcs import TestSrcRTL
from pymtl3.stdlib.test.test_sinks import TestSinkRTL
from pymtl3.stdlib.test import TestVectorSimulator
from pymtl3.stdlib.rtl.queues import NormalQueueRTL, BypassQueueRTL, PipeQueueRTL

from router.InputUnitStrFwdRTL import InputUnitStrFwdRTL

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
    if tv[5] != '?': assert dut.give.msg == tv[5]

  # Run the test

  sim = TestVectorSimulator( dut, test_vectors, tv_in, tv_out )
  sim.run_test()

def test_pipe_Bits():

  run_tv_test( InputUnitStrFwdRTL( Bits32 ), [
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
    s.dut  = InputUnitStrFwdRTL ( MsgType )
    s.sink = TestSinkRTL  ( MsgType, sink_msgs )

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
    return "{} >>> {} >>> {}".format(
      s.src.line_trace(),
      s.dut.line_trace(),
      s.sink.line_trace(),
    )

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

from .InputUnitCL_test import InputUnitCL_Tests as BaseTests

class InputUnitStrFwdRTL_Tests( BaseTests ):

  @classmethod
  def setup_class( cls ):
    cls.TestHarness = TestHarness
    cls.qtypes      = [ NormalQueueRTL, BypassQueueRTL, PipeQueueRTL ]
