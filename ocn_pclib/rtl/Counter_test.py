"""
==========================================================================
 Counter_test.py
==========================================================================
Tests for simple counter.

Author : Yanghui Ou
  Date : June 13, 2019
"""

from pymtl3 import *
from Counter import Counter

def test_simple():
  print
  dut = Counter( Bits4, reset_value=9 )
  dut.apply( SimpleSim )
  dut.incr = b1(0)
  dut.decr = b1(0)
  dut.load = b1(0)
  dut.load = b4(0)

  dut.sim_reset()
  print dut.line_trace()
  dut.incr = b1(1)
  dut.tick()
  print dut.line_trace()
  assert dut.count == b4(10)
  dut.tick()
  print dut.line_trace()
  assert dut.count == b4(11)
  dut.tick()
  print dut.line_trace()
  assert dut.count == b4(12)

  dut.decr = b1(1)
  dut.tick()
  print dut.line_trace()
  assert dut.count == b4(12)

  dut.incr = b1(0)
  dut.tick()
  print dut.line_trace()
  assert dut.count == b4(11)
  dut.tick()
  print dut.line_trace()
  assert dut.count == b4(10)
  dut.tick()
  print dut.line_trace()
  assert dut.count == b4(9)

def test_load():
  print
  dut = Counter( Bits4, reset_value=9 )
  dut.apply( SimpleSim )
  dut.incr = b1(0)
  dut.decr = b1(0)
  dut.load = b1(0)
  dut.load = b4(0)

  dut.sim_reset()
  print dut.line_trace()
  dut.incr = b1(1)
  dut.load = b1(1)
  dut.load_value = b4(3)
  dut.tick()
  print dut.line_trace()
  assert dut.count == b4(3)
  dut.load = b1(0)
  dut.tick()
  print dut.line_trace()
  assert dut.count == b4(4)
  dut.tick()
  print dut.line_trace()
  assert dut.count == b4(5)

  dut.decr = b1(1)
  dut.tick()
  print dut.line_trace()
  assert dut.count == b4(5)

  dut.incr = b1(0)
  dut.tick()
  print dut.line_trace()
  assert dut.count == b4(4)
  dut.tick()
  print dut.line_trace()
  assert dut.count == b4(3)
  dut.tick()
  print dut.line_trace()
  assert dut.count == b4(2)