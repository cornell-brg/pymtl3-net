'''
==========================================================================
SwitchUnitGrantHoldValRdy_test.py
==========================================================================

Author : Yanghui Ou
  Date : Oct 5, 2020
'''
from pymtl3 import *
from ..SwitchUnitGrantHoldValRdy import SwitchUnitGrantHoldValRdy

def test_sanity_check():
  dut = SwitchUnitGrantHoldValRdy( Bits16, num_inports=5 )
  dut.elaborate()
  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()

#-------------------------------------------------------------------------
# test_adhoc
#-------------------------------------------------------------------------
# A simple adhoc test. Port0 sends 2 packets, [ face, b000c, 8bad, f00d ]
# and [ c001 ]; while port1 sends one packet [ dead, beef ].

def test_adhoc():
  dut = SwitchUnitGrantHoldValRdy( Bits16, num_inports=5 )
  dut.elaborate()
  dut.apply( DefaultPassGroup() )
  dut.sim_reset()

  # Cycle 1 - first flit, no competitor
  dut.in_[0].val @= 1
  dut.in_[0].msg @= 0xface
  dut.hold[0]    @= 0
  dut.out.rdy    @= 1
  dut.sim_eval_combinational()
  assert dut.out.val
  assert dut.out.msg == 0xface
  dut.sim_tick()

  # Cycle 2 - second flit, set hold logic, another flit comes in
  dut.in_[0].val @= 1
  dut.in_[0].msg @= 0xb00c
  dut.hold[0]    @= 1

  dut.in_[1].val @= 1
  dut.in_[1].msg @= 0x0001
  dut.hold[1]    @= 0

  dut.out.rdy    @= 1

  dut.sim_eval_combinational()
  assert dut.out.val
  assert dut.out.msg == 0xb00c

  dut.sim_tick()

  # Cycle 3 - third flit from port0
  dut.in_[0].val @= 1
  dut.in_[0].msg @= 0x8bad
  dut.hold[0]    @= 1

  dut.in_[1].val @= 1
  dut.in_[1].msg @= 0xdead
  dut.hold[1]    @= 0

  dut.out.rdy    @= 1
  dut.sim_eval_combinational()
  assert dut.out.val
  assert dut.out.msg == 0x8bad
  dut.sim_tick()

  # Cycle 4 - last flit from port0
  dut.in_[0].val @= 1
  dut.in_[0].msg @= 0xf00d
  dut.hold[0]    @= 1

  dut.in_[1].val @= 1
  dut.in_[1].msg @= 0xdead
  dut.hold[1]    @= 0

  dut.out.rdy    @= 1
  dut.sim_eval_combinational()
  assert dut.out.val
  assert dut.out.msg == 0xf00d
  dut.sim_tick()

  # Cycle 5 - arbitrate header
  dut.in_[0].val @= 1
  dut.in_[0].msg @= 0xc001
  dut.hold[0]    @= 0

  dut.in_[1].val @= 1
  dut.in_[1].msg @= 0xdead
  dut.hold[1]    @= 0

  dut.out.rdy    @= 1
  dut.sim_eval_combinational()
  assert dut.out.val
  assert dut.out.msg == 0xdead
  dut.sim_tick()

  # Cycle 5 - arbitrate header
  dut.in_[0].val @= 1
  dut.in_[0].msg @= 0xc001
  dut.hold[0]    @= 0

  dut.in_[1].val @= 1
  dut.in_[1].msg @= 0xbeef
  dut.hold[1]    @= 1

  dut.out.rdy    @= 1
  dut.sim_eval_combinational()
  assert dut.out.val
  assert dut.out.msg == 0xbeef
  dut.sim_tick()

  # Cycle 6 - single flit packet from port0
  dut.in_[0].val @= 1
  dut.in_[0].msg @= 0xc001
  dut.hold[0]    @= 0

  dut.in_[1].val @= 0
  dut.in_[1].msg @= 0xbeef
  dut.hold[1]    @= 0

  dut.out.rdy    @= 1
  dut.sim_eval_combinational()
  assert dut.out.val
  assert dut.out.msg == 0xc001
  dut.sim_tick()

