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
  dut.sim_tick()

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

  # Cycle 1 - first flit, no competitor
  dut.get[0].rdy @= 1
  dut.get[0].ret @= 0xface
  dut.hold[0]    @= 0
  dut.give.en    @= 1
  dut.sim_eval_combinational()
  assert dut.give.rdy
  assert dut.give.ret == 0xface
  dut.sim_tick()

  # Cycle 2 - second flit, set hold logic, another flit comes in
  dut.get[0].rdy @= 1
  dut.get[0].ret @= 0xb00c
  dut.hold[0]    @= 1

  dut.get[1].rdy @= 1
  dut.get[1].ret @= 0x0001
  dut.hold[1]    @= 0

  dut.give.en    @= 1

  dut.sim_eval_combinational()
  assert dut.give.rdy
  assert dut.give.ret == 0xb00c

  dut.sim_tick()

  # Cycle 3 - third flit from port0
  dut.get[0].rdy @= 1
  dut.get[0].ret @= 0x8bad
  dut.hold[0]    @= 1

  dut.get[1].rdy @= 1
  dut.get[1].ret @= 0xdead
  dut.hold[1]    @= 0

  dut.give.en    @= 1
  dut.sim_eval_combinational()
  assert dut.give.rdy
  assert dut.give.ret == 0x8bad
  dut.sim_tick()

  # Cycle 4 - last flit from port0
  dut.get[0].rdy @= 1
  dut.get[0].ret @= 0xf00d
  dut.hold[0]    @= 1

  dut.get[1].rdy @= 1
  dut.get[1].ret @= 0xdead
  dut.hold[1]    @= 0

  dut.give.en    @= 1
  dut.sim_eval_combinational()
  assert dut.give.rdy
  assert dut.give.ret == 0xf00d
  dut.sim_tick()

  # Cycle 5 - arbitrate header
  dut.get[0].rdy @= 1
  dut.get[0].ret @= 0xc001
  dut.hold[0]    @= 0

  dut.get[1].rdy @= 1
  dut.get[1].ret @= 0xdead
  dut.hold[1]    @= 0

  dut.give.en    @= 1
  dut.sim_eval_combinational()
  assert dut.give.rdy
  assert dut.give.ret == 0xdead
  dut.sim_tick()

  # Cycle 5 - arbitrate header
  dut.get[0].rdy @= 1
  dut.get[0].ret @= 0xc001
  dut.hold[0]    @= 0

  dut.get[1].rdy @= 1
  dut.get[1].ret @= 0xbeef
  dut.hold[1]    @= 1

  dut.give.en    @= 1
  dut.sim_eval_combinational()
  assert dut.give.rdy
  assert dut.give.ret == 0xbeef
  dut.sim_tick()

  # Cycle 6 - single flit packet from port0
  dut.get[0].rdy @= 1
  dut.get[0].ret @= 0xc001
  dut.hold[0]    @= 0

  dut.get[1].rdy @= 0
  dut.get[1].ret @= 0xbeef
  dut.hold[1]    @= 0

  dut.give.en    @= 1
  dut.sim_eval_combinational()
  assert dut.give.rdy
  assert dut.give.ret == 0xc001
  dut.sim_tick()

