"""
=========================================================================
OutputUnitCL_test.py
=========================================================================
Test cases for OutputUnitCL.

Author : Yanghui Ou
  Date : Feb 28, 2019
"""
import pytest
import hypothesis
from hypothesis import strategies as st

from pymtl3 import *
from pymtl3.passes.PassGroups import SimpleSim
from pymtl3.stdlib.test.test_srcs import TestSrcCL
from pymtl3.stdlib.test.test_sinks import TestSinkCL
from pymtl3.stdlib.cl.queues import NormalQueueCL, BypassQueueCL, PipeQueueCL
from pymtl3.datatypes import strategies as pst

from router.OutputUnitCL import OutputUnitCL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, MsgType, src_msgs, sink_msgs ):

    s.src   = TestSrcCL( MsgType, src_msgs  )
    s.src_q = BypassQueueCL( num_entries=1 )
    s.dut   = OutputUnitCL( MsgType )
    s.sink  = TestSinkCL( MsgType, sink_msgs )

    # Connections
    s.connect( s.src.send,  s.src_q.enq )
    s.connect( s.src_q.deq, s.dut.get   )
    s.connect( s.dut.send, s.sink.recv  )

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return "{} {} {}".format(
      s.src.line_trace(),
      s.dut.line_trace(),
      s.sink.line_trace(),
    )

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

from .InputUnitCL_test import InputUnitCL_Tests as BaseTests

class OutputUnitCL_Tests( BaseTests ):

  @classmethod
  def setup_class( cls ):
    cls.TestHarness = TestHarness
    cls.qtypes      = [ NormalQueueCL, BypassQueueCL, PipeQueueCL ]