"""
==========================================================================
InputUnitCL_test.py
==========================================================================
Test cases for InputUnitCL.

Author: Yanghui Ou
  Date: May 16, 2019
"""
import hypothesis
import pytest
from hypothesis import strategies as st

from ocnlib.utils import run_sim
from pymtl3 import *
from pymtl3.datatypes import strategies as pst
from pymtl3.stdlib.queues import BypassQueueCL, NormalQueueCL, PipeQueueCL
from pymtl3.stdlib.test_utils.test_sinks import TestSinkCL
from pymtl3.stdlib.test_utils.test_srcs import TestSrcCL
from router.InputUnitCL import InputUnitCL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, MsgType, src_msgs, sink_msgs ):

    s.src  = TestSrcCL  ( MsgType, src_msgs  )
    s.sink = TestSinkCL ( MsgType, sink_msgs )
    s.dut  = InputUnitCL( MsgType )

    # Connections
    s.src.send //= s.dut.recv

    @update_once
    def up_give_en():
      if s.dut.give.rdy() and s.sink.recv.rdy():
        s.sink.recv( s.dut.give() )

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

class InputUnitCL_Tests:

  @classmethod
  def setup_class( cls ):
    cls.TestHarness = TestHarness
    cls.qtypes      = [ NormalQueueCL, BypassQueueCL, PipeQueueCL ]

  def test_normal2_simple( s ):
    test_msgs = [ b16( 4 ), b16( 1 ), b16( 2 ), b16( 3 ) ]
    arrival_time = [ 2, 3, 4, 5 ]
    th = s.TestHarness( Bits16, test_msgs, test_msgs )
    th.set_param( "top.sink.construct", arrival_time=arrival_time )
    run_sim( th )

  def test_hypothesis( s ):
    @hypothesis.settings( deadline=None )
    @hypothesis.given(
      qsize     = st.integers(1, 16),
      dwid      = st.integers(1, 32),
      sink_init = st.integers(0, 20),
      qtype     = st.sampled_from( s.qtypes ),
      test_msgs = st.data(),
    )
    def actual_test( dwid, qsize, qtype, sink_init, test_msgs ):
      msgs = test_msgs.draw( st.lists( pst.bits(dwid), min_size=1, max_size=100 ) )
      th = s.TestHarness( mk_bits(dwid), msgs, msgs )
      th.set_param( "top.sink.construct", initial_delay=sink_init )
      th.set_param( "top.dut.construct", QueueType = qtype )
      th.set_param( "top.dut.queue.construct", num_entries=qsize )
      run_sim( th, max_cycles=5000 )
    actual_test()
