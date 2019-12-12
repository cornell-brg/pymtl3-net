"""
=========================================================================
SwitchUnitRTL_test.py
=========================================================================
Test for SwitchUnitRTL.

 Author : Yanghui Ou, Cheng Tan
   Date : June 22, 2019
"""
from ocn_pclib.ifcs.packets import mk_generic_pkt
from pymtl3 import *
from pymtl3.stdlib.test.test_sinks import TestSinkCL
from pymtl3.stdlib.test.test_srcs import TestSrcCL
from router.SwitchUnitRTL import SwitchUnitRTL

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

def test_switch_unit_simpe():
  dut = SwitchUnitRTL( Bits32, num_inports=5 )
  dut.elaborate()
  dut.apply( SimulationPass() )
  dut.sim_reset()

  print("")
  dut.get[0].rdy = b1(1)
  dut.get[0].msg = b32(0xfaceb00c)
  dut.get[1].rdy = b1(1)
  dut.get[1].msg = b32(0xdeadface)
  dut.get[4].rdy = b1(1)
  dut.get[4].msg = b32(0xbaadbeef)
  dut.give.en = b1(0)
  dut.eval_combinational()
  dut.tick()
  print( dut.line_trace() )

  for i in range( 3 ):
    assert dut.give.rdy
    assert dut.give.msg in { b32(0xfaceb00c), b32(0xdeadface), b32(0xbaadbeef)  }
    dut.give.en = b1(1)
    dut.eval_combinational()
    dut.tick()
    print( dut.line_trace() )
