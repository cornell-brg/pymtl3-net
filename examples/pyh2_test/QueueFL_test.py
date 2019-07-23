"""
==========================================================================
QueueFL_test.py
==========================================================================
Tests for QueueFL.

Author : Yanghui Ou
  Date : July 12, 2019
"""
from __future__ import absolute_import, division, print_function

from pymtl3 import *

from .QueueFL import QueueFL

def test_adhoc_fl():
  dut = QueueFL( num_entries=2 )
  dut.elaborate()
  dut.apply( SimulationPass )
  assert dut.enq.rdy()
  dut.enq( b16(0xface) )
  assert dut.enq.rdy()
  dut.enq( b16(0xbabe) )
  assert not dut.enq.rdy()
  assert dut.deq.rdy()
  assert dut.deq() == 0xface
  assert dut.deq.rdy()
  assert dut.deq() == 0xbabe

