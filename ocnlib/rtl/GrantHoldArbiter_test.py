'''
==========================================================================
GrantHoldArbiter_test.py
==========================================================================

Author : Yanghui Ou
  Date : Jan 22, 2020
'''
from pymtl3 import *
from .GrantHoldArbiter import GrantHoldArbiter


def test_simple():
  arb = GrantHoldArbiter( nreqs=4 )
  arb.elaborate()
  arb.apply( SimulationPass() )
  arb.sim_reset()

  arb.reqs @= 0b0011
  arb.hold @= 0
  arb.sim_tick()

  g0 = arb.grants.clone()
  arb.sim_tick()

  arb.hold @= 1
  arb.sim_eval_combinational()
  assert arb.grants == g0
  arb.sim_tick()

