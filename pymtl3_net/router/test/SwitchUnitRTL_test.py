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

from pymtl3_net.router.SwitchUnitRTL import SwitchUnitRTL
from pymtl3_net.ocnlib.ifcs.packets import mk_generic_pkt

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

def test_switch_unit_simple():
  dut = SwitchUnitRTL( Bits32, num_inports=5 )
  dut.elaborate()
  dut.apply( DefaultPassGroup(linetrace=True) )
  dut.sim_reset()

  dut.recv[0].val @= 1
  dut.recv[0].msg @= 0xfaceb00c
  dut.recv[1].val @= 1
  dut.recv[1].msg @= 0xdeadface
  dut.recv[4].val @= 1
  dut.recv[4].msg @= 0xbaadbeef
  dut.send.rdy@= 0
  dut.sim_eval_combinational()
  dut.sim_tick()

  for i in range( 3 ):
    dut.send.rdy @= 1
    dut.sim_eval_combinational()

    assert dut.send.rdy
    assert dut.send.msg in { b32(0xfaceb00c), b32(0xdeadface), b32(0xbaadbeef)  }
    dut.sim_tick()

