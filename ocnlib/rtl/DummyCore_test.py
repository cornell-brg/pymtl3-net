'''
==========================================================================
DummyCore_test.py
==========================================================================
Simple test for DummyCore.

Author : Yanghui Ou
  Date : July 21, 2020
'''
from pymtl3 import *
from .DummyCore import DummyCore

@bitstruct
class TestHeader:
  src_x : Bits8
  src_y : Bits8
  dst_x : Bits8
  dst_y : Bits8
  dummy : Bits32

def test_sanity_check():
  dut = DummyCore( TestHeader )
  dut.elaborate()
  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()
  dut.sim_tick()
