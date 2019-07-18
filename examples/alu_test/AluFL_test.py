"""
==========================================================================
AluFL_test.py
==========================================================================
Tests for AluFL.

Author : Cheng Tan
  Date : July 18, 2019
"""
from __future__ import absolute_import, division, print_function

from pymtl3 import *

from AluFL import AluFL
from AluVRTL_test import mk_alu_req, mk_alu_resp

def test_adhoc_fl():
  nbits = 16
  ReqType  = mk_alu_req ( nbits )
  RespType = mk_alu_resp( nbits )

  dut = AluFL( RespType )
  dut.elaborate()
  dut.apply( SimulationPass )
  print()

  print( dut.line_trace() )
  assert dut.enq.rdy()
  req = ReqType( 0x0003, 0x0005, 0b000)
  dut.enq( req )
  print( dut.line_trace() )

  assert not dut.enq.rdy()
  assert dut.deq.rdy()
  out = dut.deq()
  assert not dut.deq.rdy()

  print (out)
  assert out.result == b16( 8 )
  assert out.branch == b1 ( 0 )
