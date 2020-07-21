'''
==========================================================================
DummyNode_test.py
==========================================================================
Simple test for DummyNode.

Author : Yanghui Ou
  Date : July 20, 2020
'''
from pymtl3 import *
from .DummyNode import DummyNode

@bitstruct
class TestHeader:
  src_x : Bits8
  src_y : Bits8
  dst_x : Bits8
  dst_y : Bits8
  dummy : Bits32

def test_sanity_check():
  dut = DummyNode( TestHeader )
  dut.elaborate()
  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()
  dut.sim_tick()
