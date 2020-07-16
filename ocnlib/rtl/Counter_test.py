"""
==========================================================================
 Counter_test.py
==========================================================================
Tests for simple counter.

Author : Yanghui Ou
  Date : June 13, 2019
"""

from pymtl3 import *

from .Counter import Counter


def test_simple():
  dut = Counter( Bits4, reset_value=9 )
  dut.apply( DefaultPassGroup(print_line_trace=True) )
  dut.sim_reset()

  dut.incr @= 1
  dut.decr @= 0
  dut.load @= 0

  dut.sim_tick()
  assert dut.count == b4(10)
  dut.sim_tick()
  assert dut.count == b4(11)
  dut.sim_tick()
  assert dut.count == b4(12)

  dut.decr @= 1
  dut.sim_tick()
  assert dut.count == b4(12)

  dut.incr @= 0
  dut.sim_tick()
  assert dut.count == b4(11)
  dut.sim_tick()
  assert dut.count == b4(10)
  dut.sim_tick()
  assert dut.count == b4(9)

def test_load():
  dut = Counter( Bits4, reset_value=9 )
  dut.apply( DefaultPassGroup(print_line_trace=True) )

  dut.sim_reset()

  dut.incr @= 1
  dut.decr @= 0
  dut.load @= 1
  dut.load_value @= 3
  dut.sim_tick()
  assert dut.count == b4(3)
  dut.load @= 0
  dut.sim_tick()
  assert dut.count == b4(4)
  dut.sim_tick()
  assert dut.count == b4(5)

  dut.decr @= 1
  dut.sim_tick()
  assert dut.count == b4(5)

  dut.incr @= 0
  dut.sim_tick()
  assert dut.count == b4(4)
  dut.sim_tick()
  assert dut.count == b4(3)
  dut.sim_tick()
  assert dut.count == b4(2)
