import tempfile
from pymtl                import *
from pclib.test           import TestVectorSimulator
from pc.GrantHoldArbiter import GrantHoldArbiter
from hypothesis.stateful import * 
from hypothesis import strategies as st

def run_test( model, test_vectors ):
 
  model.elaborate()

  def tv_in( dut, test_vector ):
    dut.reqs.value = test_vector[0]
    dut.reqs.value = test_vector[0]
    dut.reqs.value = test_vector[0]

  def tv_out( model, test_vector ):
    assert model.grants == test_vector[2]
  
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

def test_arb_4_directed( dump_vcd, test_verilog ):
  model = GrantHoldArbiter( 4 )
  model.vcd_file = dump_vcd
  if test_verilog:
    model = TranslationTool( model )

  run_test( model, [
    # reqs    hold grants      priority
    [ 0b0000, 0,   0b0000 ], # 0001
    [ 0b1000, 0,   0b1000 ], # 0001
    [ 0b1100, 0,   0b0100 ], # 0100  
    [ 0b1100, 0,   0b1000 ], # 1000
    [ 0b0000, 1,   0b1000 ], # 1000
    [ 0b0111, 0,   0b0001 ], # 1000
    [ 0b1111, 0,   0b0010 ], # 0010
    [ 0b1111, 1,   0b0010 ], # 0010
    [ 0b1111, 1,   0b0010 ], # 0010
  ] )

