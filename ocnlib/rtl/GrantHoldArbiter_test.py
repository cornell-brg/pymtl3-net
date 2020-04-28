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
  arb.tick()

  print()
  arb.reqs = b4(0b0011)
  arb.hold = b1(0)
  arb.en   = b1(1)
  arb.eval_combinational()
  print( arb.line_trace() )
  arb.tick()
  
  arb.eval_combinational()
  print( arb.line_trace() )
  g0 = b4(arb.grants)
  arb.tick()

  arb.hold = b1(1)
  arb.en   = b1(0)
  arb.eval_combinational()
  print( arb.line_trace() )
  assert arb.grants == g0
  arb.tick()

