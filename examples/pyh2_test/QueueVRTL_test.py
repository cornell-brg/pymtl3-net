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
from pymtl3.passes import GenDAGPass, OpenLoopCLPass
from pymtl3.passes.sverilog import ImportPass
from pymtl3.stdlib.cl.queues import NormalQueueCL
from pymtl3.stdlib.rtl.queues import NormalQueueRTL
from pymtl3.stdlib.ifcs import DeqIfcRTL, EnqIfcRTL
from pymtl3.stdlib.test.test_sinks import TestSinkCL, TestSinkRTL
from pymtl3.stdlib.test.test_srcs import TestSrcCL
from pymtl3.stdlib.test.pyh2.stateful import run_pyh2
from pymtl3.stdlib.test.pyh2.RTL2CLWrapper import RTL2CLWrapper
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

class TestHarnessWrapped( Component ):

  def construct( s, MsgType, QType, src_msgs, sink_msgs ):

    s.src  = TestSrcCL( MsgType, src_msgs )
    s.dut  = RTL2CLWrapper( QType(), { 'enq': None, 'deq': None } )
    s.sink = TestSinkCL( MsgType, sink_msgs )

    s.connect( s.src.send, s.dut.enq   )

    @s.update
    def up_deq_recv():
      if s.dut.deq.rdy() and s.sink.recv.rdy():
        s.sink.recv( s.dut.deq() )

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
  print( "SCHEDULE:", th._sched.schedule )
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

def test_simple():
  test_msgs = [ b32(4), b32(1), b32(2), b32(3), b32(4), b32(5) ]
  th = TestHarness( Bits32, QueueVRTL, test_msgs, test_msgs )
  run_sim( th )

def test_simple_wrapped():
  test_msgs = [ b32(4), b32(1), b32(2), b32(3), b32(4), b32(5) ]
  th = TestHarnessWrapped( Bits32, QueueVRTL, test_msgs, test_msgs )
  run_sim( th )

def test_openloop():
  print()
  dut = RTL2CLWrapper( QueueVRTL(), { 'enq': None, 'deq': None } )
  dut.elaborate()
  dut = ImportPass()( dut )
  dut.elaborate()
  dut.apply( GenDAGPass() )
  dut.apply( OpenLoopCLPass() )
  dut.lock_in_simulation()
  dut.tick()
  dut.tick()
  dut.sim_reset()
  dut.tick()
  assert dut.enq.rdy()
  dut.enq( 0x1111 )
  assert dut.enq.rdy()
  dut.enq( 0x2222 )

#-------------------------------------------------------------------------
# PyH2 test
#-------------------------------------------------------------------------

def test_pyh2():
  # sv_q = QueueVRTL()
  sv_q = NormalQueueRTL( Bits32, num_entries=2 )
  cl_q = NormalQueueCL( num_entries=2 )
  run_pyh2( sv_q, cl_q )
