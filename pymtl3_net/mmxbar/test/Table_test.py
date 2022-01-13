'''
==========================================================================
Table_test.py
==========================================================================
Unit tests for the table data structure.

Author : Yanghui Ou
  Date : Apr 10, 2020
'''
from pymtl3 import *
from ..Table import Table

def test_sanity_check():
  dut = Table( Bits8, 8 )
  dut.elaborate()
  dut.apply( DefaultPassGroup( linetrace=True ) )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()
  dut.sim_tick()

def test_adhoc_8( cmdline_opts ):
  print()
  dut = Table( Bits8, 4 )
  dut.elaborate()
  dut.apply( DefaultPassGroup( linetrace=True ) )
  dut.sim_reset()

  # Cycle 1

  dut.sim_tick()
  assert dut.alloc.rdy
  assert ~dut.dealloc.rdy

  dut.alloc.en  @= b1(1)
  dut.alloc.msg @= b8(0x11)

  dut.sim_eval_combinational()
  dut.print_line_trace()
  assert dut.alloc.ret == 3

  # Cycle 2

  dut.sim_tick()
  assert dut.alloc.rdy
  assert dut.dealloc.rdy

  dut.alloc.en  @= b1(1)
  dut.alloc.msg @= b8(0x10)

  dut.sim_eval_combinational()
  dut.print_line_trace()
  assert dut.alloc.ret == 2

  # Cycle 3

  dut.sim_tick()
  assert dut.alloc.rdy
  assert dut.dealloc.rdy

  dut.alloc.en  @= b1(1)
  dut.alloc.msg @= b8(0x01)

  dut.sim_eval_combinational()
  dut.print_line_trace()
  assert dut.alloc.ret == 1

  # Cycle 4

  dut.sim_tick()
  assert dut.alloc.rdy
  assert dut.dealloc.rdy

  dut.alloc.en  @= b1(1)
  dut.alloc.msg @= b8(0x00)

  dut.sim_eval_combinational()
  dut.print_line_trace()
  assert dut.alloc.ret == 0

  # Cycle 5

  dut.sim_tick()
  assert ~dut.alloc.rdy
  assert dut.dealloc.rdy

  dut.alloc.en    @= b1(0)
  dut.dealloc.en  @= b1(1)
  dut.dealloc.msg @= b2(1)

  dut.sim_eval_combinational()
  dut.print_line_trace()
  assert dut.dealloc.ret == b8(0x01)

  # Cycle 6

  dut.sim_tick()
  assert dut.alloc.rdy
  assert dut.dealloc.rdy

  dut.alloc.en    @= b1(1)
  dut.dealloc.en  @= b1(1)
  dut.dealloc.msg @= b2(2)

  dut.sim_eval_combinational()
  dut.print_line_trace()
  assert dut.dealloc.ret == b8(0x10)
  assert dut.alloc.ret   == 1
