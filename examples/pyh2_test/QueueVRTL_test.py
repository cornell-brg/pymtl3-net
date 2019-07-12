"""
==========================================================================
QueueVRTL_test.py
==========================================================================
Imported Queue from SystemVerilog.

Author : Yanghui Ou
  Date : July 10, 2019
"""
from __future__ import absolute_import, division, print_function

from pymtl3 import *
from pymtl3.dsl import Placeholder
from pymtl3.passes.sverilog import ImportPass
from pymtl3.stdlib.cl.queues import NormalQueueCL
from pymtl3.stdlib.ifcs import DeqIfcRTL, EnqIfcRTL
from pymtl3.stdlib.test.test_sinks import TestSinkRTL
from pymtl3.stdlib.test.test_srcs import TestSrcCL
from pymtl3.stdlib.test.pyh2.stateful import run_pyh2

from .QueueVRTL import Queue, QueueVRTL


def test_import_direct():
  top = Queue()
  top.elaborate()
  top.sverilog_import = True
  top.sverilog_import_path = "../Queue.sv"
  top = ImportPass()( top )

def test_import_wrap():
  top = QueueVRTL()
  top.elaborate()
  top.q.sverilog_import = True
  top.q.sverilog_import_path = "../Queue.sv"
  top = ImportPass()( top )

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, MsgType, QType, src_msgs, sink_msgs ):

    s.src  = TestSrcCL ( MsgType, src_msgs )
    s.dut  = QType()
    s.sink = TestSinkRTL( MsgType, sink_msgs )

    s.connect( s.src.send, s.dut.enq   )
    s.connect( s.dut.deq,  s.sink.recv )

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return "{} ({}) {}".format(
      s.src.line_trace(), s.dut.line_trace(), s.sink.line_trace() )

#-------------------------------------------------------------------------
# run_sim
#-------------------------------------------------------------------------

def run_sim( th, max_cycles=100 ):

  # Create a simulator
  th.elaborate()
  th = ImportPass()( th )
  th.elaborate()
  th.apply( SimulationPass )
  th.sim_reset()

  print("")
  ncycles = 0
  print("{:2}:{}".format( ncycles, th.line_trace() ))
  while not th.done() and ncycles < max_cycles:
    th.tick()
    ncycles += 1
    print("{:2}:{}".format( ncycles, th.line_trace() ))

  # Check timeout
  assert ncycles < max_cycles

  th.tick()
  th.tick()
  th.tick()

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

test_msgs = [ Bits32( 4 ), Bits32( 1 ), Bits32( 2 ), Bits32( 3 ) ]

def test_normal1_simple():
  th = TestHarness( Bits32, QueueVRTL, test_msgs, test_msgs )
  run_sim( th )

#-------------------------------------------------------------------------
# PyH2 test
#-------------------------------------------------------------------------

def test_pyh2():
  sv_q = QueueVRTL()
  cl_q = NormalQueueCL( num_entries=2 )
  run_pyh2( sv_q, cl_q )
