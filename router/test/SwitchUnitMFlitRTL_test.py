'''
==========================================================================
SwitchUnitMFlitRTL_test.py
==========================================================================

Author : Yanghui Ou
  Date : Jan 28, 2020
'''
from pymtl3 import *
from ..SwitchUnitMFlitRTL import SwitchUnitMFlitRTL

def test_sanity_check():

  class DummyFormat:
    PLEN = slice(0, 8)

  dut = SwitchUnitMFlitRTL( DummyFormat, Bits64, num_inports=5 )
  dut.elaborate()
  dut.apply( SimulationPass() )
  dut.sim_reset()
  dut.tick()