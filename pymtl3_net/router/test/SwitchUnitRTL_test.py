"""
=========================================================================
SwitchUnitRTL_test.py
=========================================================================
Test for SwitchUnitRTL.

 Author : Yanghui Ou, Cheng Tan
   Date : June 22, 2019
"""
from pymtl3 import *
from pymtl3.stdlib.test_utils.test_sinks import TestSinkCL
from pymtl3.stdlib.test_utils.test_srcs import TestSrcCL
from router.SwitchUnitRTL import SwitchUnitRTL
from ocnlib.ifcs.packets import mk_generic_pkt

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

def test_switch_unit_simple():
  dut = SwitchUnitRTL( Bits32, num_inports=5 )
  dut.elaborate()
  dut.apply( DefaultPassGroup() )
  dut.sim_reset()

  dut.get[0].rdy @= 1
  dut.get[0].ret @= 0xfaceb00c
  dut.get[1].rdy @= 1
  dut.get[1].ret @= 0xdeadface
  dut.get[4].rdy @= 1
  dut.get[4].ret @= 0xbaadbeef
  dut.give.en @= 0
  dut.sim_eval_combinational()
  dut.sim_tick()

  for i in range( 3 ):
    dut.give.en @= 1
    dut.sim_eval_combinational()

    assert dut.give.rdy
    assert dut.give.ret in { b32(0xfaceb00c), b32(0xdeadface), b32(0xbaadbeef)  }
    dut.sim_tick()
