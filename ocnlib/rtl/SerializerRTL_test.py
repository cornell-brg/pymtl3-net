'''
==========================================================================
SerializerRTL_test.py
==========================================================================
Unit tests for SerializerRTL.

Author : Yanghui Ou
  Date : Feb 26, 2020
'''
from pymtl3 import *
from .SerializerRTL import SerializerRTL

def test_sanity_check():
  dut = SerializerRTL( out_nbits=16, max_nblocks=4 )
  dut.elaborate()
  dut.apply( SimulationPass() )
  dut.sim_reset()
  dut.tick()
  dut.tick()
