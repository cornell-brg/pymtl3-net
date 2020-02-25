'''
==========================================================================
SwitchUnitGrantHoldRTL_test.py
==========================================================================

Author : Yanghui Ou
  Date : Jan 28, 2020
'''
from pymtl3 import *
from ..SwitchUnitGrantHoldRTL import SwitchUnitGrantHoldRTL

def test_sanity_check():
  dut = SwitchUnitGrantHoldRTL( Bits16, num_inports=5 )
  dut.elaborate()
  dut.apply( SimulationPass() )
  dut.sim_reset()
  dut.tick()

#-------------------------------------------------------------------------
# test_adhoc
#-------------------------------------------------------------------------
# A simple adhoc test. Port0 sends 2 packets, [ face, b000c, 8bad, f00d ]
# and [ c001 ]; while port1 sends one packet [ dead, beef ].

def test_adhoc():
  dut = SwitchUnitGrantHoldRTL( Bits16, num_inports=5 )
  dut.elaborate()
  dut.apply( SimulationPass() )
  dut.sim_reset()
  print()

  # Cycle 1 - first flit, no competitor
  dut.get[0].rdy = b1(1)
  dut.get[0].ret = b16( 0xface )
  dut.hold[0]    = b1(0)
  dut.give.en    = b1(1)
  dut.eval_combinational()
  assert dut.give.rdy
  assert dut.give.ret == 0xface
  print( dut.line_trace() )
  dut.tick()

  # Cycle 2 - second flit, set hold logic, another flit comes in
  dut.get[0].rdy = b1(1)
  dut.get[0].ret = b16( 0xb00c )
  dut.hold[0]    = b1(1)

  dut.get[1].rdy = b1(1)
  dut.get[1].ret = b16( 0x0001 )
  dut.hold[1]    = b1(0)

  dut.give.en    = b1(1)
  dut.eval_combinational()
  print( dut.line_trace() )
  assert dut.give.rdy
  assert dut.give.ret == 0xb00c
  dut.tick()

  # Cycle 3 - third flit from port0
  dut.get[0].rdy = b1(1)
  dut.get[0].ret = b16( 0x8bad )
  dut.hold[0]    = b1(1)

  dut.get[1].rdy = b1(1)
  dut.get[1].ret = b16( 0xdead )
  dut.hold[1]    = b1(0)

  dut.give.en    = b1(1)
  dut.eval_combinational()
  print( dut.line_trace() )
  assert dut.give.rdy
  assert dut.give.ret == 0x8bad
  dut.tick()

  # Cycle 4 - last flit from port0
  dut.get[0].rdy = b1(1)
  dut.get[0].ret = b16( 0xf00d )
  dut.hold[0]    = b1(1)

  dut.get[1].rdy = b1(1)
  dut.get[1].ret = b16( 0xdead )
  dut.hold[1]    = b1(0)

  dut.give.en    = b1(1)
  dut.eval_combinational()
  print( dut.line_trace() )
  assert dut.give.rdy
  assert dut.give.ret == 0xf00d
  dut.tick()

  # Cycle 5 - arbitrate header
  dut.get[0].rdy = b1(1)
  dut.get[0].ret = b16( 0xc001 )
  dut.hold[0]    = b1(0)

  dut.get[1].rdy = b1(1)
  dut.get[1].ret = b16( 0xdead )
  dut.hold[1]    = b1(0)

  dut.give.en    = b1(1)
  dut.eval_combinational()
  print( dut.line_trace() )
  assert dut.give.rdy
  assert dut.give.ret == 0xdead
  dut.tick()

  # Cycle 5 - arbitrate header
  dut.get[0].rdy = b1(1)
  dut.get[0].ret = b16( 0xc001 )
  dut.hold[0]    = b1(0)

  dut.get[1].rdy = b1(1)
  dut.get[1].ret = b16( 0xbeef )
  dut.hold[1]    = b1(1)

  dut.give.en    = b1(1)
  dut.eval_combinational()
  print( dut.line_trace() )
  assert dut.give.rdy
  assert dut.give.ret == 0xbeef
  dut.tick()

  # Cycle 6 - single flit packet from port0
  dut.get[0].rdy = b1(1)
  dut.get[0].ret = b16( 0xc001 )
  dut.hold[0]    = b1(0)

  dut.get[1].rdy = b1(0)
  dut.get[1].ret = b16( 0xbeef )
  dut.hold[1]    = b1(0)

  dut.give.en    = b1(1)
  dut.eval_combinational()
  print( dut.line_trace() )
  assert dut.give.rdy
  assert dut.give.ret == 0xc001
  dut.tick()

