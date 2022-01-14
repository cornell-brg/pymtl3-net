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
from pymtl3.stdlib.stream.queues import (BypassQueueRTL, NormalQueueRTL,
                                      PipeQueueRTL)
from pymtl3.stdlib.test_utils import TestVectorSimulator

from pymtl3.stdlib.stream.SinkRTL import SinkRTL as TestSinkRTL
from pymtl3.stdlib.stream.SourceRTL import SourceRTL as TestSrcRTL

from pymtl3_net.router.InputUnitRTL import InputUnitRTL

from .InputUnitCL_test import InputUnitCL_Tests as BaseTests

#-------------------------------------------------------------------------
# TestVectorSimulator test
#-------------------------------------------------------------------------

def run_tv_test( dut, test_vectors ):

  # Define input/output functions

  def tv_in( dut, tv ):
    dut.recv.val  @= tv[0]
    dut.recv.msg  @= tv[2]
    dut.send.rdy  @= tv[3]

  def tv_out( dut, tv ):
    if tv[1] != '?': assert dut.recv.rdy == tv[1]
    if tv[4] != '?': assert dut.send.val == tv[4]
    if tv[5] != '?': assert dut.send.msg == tv[5]

  # Run the test

  sim = TestVectorSimulator( dut, test_vectors, tv_in, tv_out )
  sim.run_test()

def test_pipe_Bits():

  run_tv_test( InputUnitRTL( Bits32 ), [
    #  enq.val  enq.rdy  enq.msg   deq.rdy  deq.val deq.msg
    [   1,      1,       123,      0,       0,      '?'  ],
    [   1,      1,       345,      0,       1,      123  ],
    [   0,      0,       567,      0,       1,      123  ],
    [   0,      0,       567,      1,       1,      123  ],
    [   0,      1,       567,      1,       1,      345  ],
    [   1,      1,       567,      0,       0,      '?'  ],
    [   1,      1,       0  ,      1,       1,      567  ],
    [   1,      1,       1  ,      1,       1,      0    ],
    [   1,      1,       2  ,      1,       1,      1    ],
    [   0,      1,       2  ,      1,       1,      2    ],
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
    s.src.send //= s.dut.recv
    s.dut.send //= s.sink.recv

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


class InputUnitRTL_Tests( BaseTests ):

  @classmethod
  def setup_class( cls ):
    cls.TestHarness = TestHarness
    cls.qtypes      = [ NormalQueueRTL, BypassQueueRTL, PipeQueueRTL ]
