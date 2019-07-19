"""
==========================================================================
FifoVRTL_test.py
==========================================================================
Imported FIFO from Verilog.

Author : Cheng Tan
  Date : July 19, 2019
"""
from __future__ import absolute_import, division, print_function

import hypothesis
from hypothesis import strategies as st

from pymtl3 import *
from pymtl3.datatypes import strategies as pst
from pymtl3.passes import GenDAGPass, OpenLoopCLPass as AutoTickSimPass
from pymtl3.passes.sverilog import ImportPass
#from pymtl3.stdlib.test.pyh2.stateful import run_pyh2
#from pymtl3.stdlib.test.pyh2.RTL2CLWrapper import RTL2CLWrapper

from FifoVRTL import Fifo, FifoVRTL
#from FifoL   import AluFL

def mk_fifo_req( nbits, els, ready ):
  DataType = mk_bits( nbits )
  new_name = 'FifoReq_{}_{}_{}'.format( nbits, els, ready )

  msg_cls = mk_bit_struct( new_name,[
      ( 'clr' , Bits1    ),
      ( 'ckpt', Bits1    ),
      ( 'roll', Bits1    ),
      ( 'data', DataType ),
      ( 'yumi', Bits1    ),
    ])
  msg_cls.data_nbits = nbits
  msg_cls.els        = els
  msg_cls.ready      = ready
  return msg_cls

def mk_fifo_resp( nbits ):
  DataType = mk_bits( nbits )
  new_name = 'FifoResp_{}'.format( nbits )

  msg_cls = mk_bit_struct( new_name,[
      ( 'data', DataType ),
    ] )
  msg_cls.data_nbits = nbits
  return msg_cls

#-------------------------------------------------------------------------
# Ad-hoc test
#-------------------------------------------------------------------------

def test_adhoc():
  ReqType  = mk_fifo_req (16, 16, 1)
  RespType = mk_fifo_resp(16)
  dut = FifoVRTL( ReqType, RespType )
  dut.elaborate()
  dut = ImportPass()( dut )
  dut.apply( SimulationPass )
  dut.sim_reset()

  print()
  print( dut.line_trace() )
  # Write a message
  dut.enq.en = b1(1)
  dut.enq.msg = ReqType(b1(0x1),b1(0x1),b1(0x1),b16(0x0002),b1(0x1))
  dut.tick()
  dut.enq.msg = ReqType(b1(0x1),b1(0x1),b1(0x1),b16(0x0003),b1(0x1))
#  assert dut.deq.rdy
  dut.deq.en = b1(1)

  print( dut.line_trace() )
  dut.tick()
  print( dut.line_trace() )
  dut.tick()
  print( dut.line_trace() )
  dut.tick()
  print( dut.line_trace() )
  dut.tick()
  print( dut.line_trace() )

  # Read a message
#  assert dut.deq.msg.result == b16(0x0005)

#-------------------------------------------------------------------------
# PyH2 test
#-------------------------------------------------------------------------

@st.composite
def alu_req_strat( draw, nbits ):
  in1 = draw( pst.bits(nbits), label="in1" )
  in2 = draw( pst.bits(nbits), label="in2" )
  op  = draw( pst.bits(3),     label='op'  )
  ReqType = mk_alu_req( nbits )
  return ReqType( in1, in2, op )

@hypothesis.settings( deadline=None )
@hypothesis.given( nbits = st.integers(1, 16) )
def ttest_pyh2( nbits ):
  print( "nbits = {}".format( nbits ) )
  Req  = mk_alu_req( nbits )
  Resp = mk_alu_resp( nbits )
  run_pyh2( AluVRTL( Req, Resp ), AluFL( Resp ), arg_strat_mapping={
    'enq.msg' : alu_req_strat( nbits )
  } )
