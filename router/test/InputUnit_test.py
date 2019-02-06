import pytest

from pymtl      import *
from pclib.test import TestVectorSimulator, TestSource, TestSink
from router.InputUnit import InputUnit

#=======================================================================
# Helper functions 
#=======================================================================
def run_iu_test( dump_vcd, test_verilog,
                 ModelType, num_entries, data_width, test_vectors ):
  """
  A helper function that runs the tests for the given input unit.
  """

  # Elaborate the model
  dut = ModelType( num_entries, data_width )
  dut.vcd_file = dump_vcd
  dut = TranslationTool( dut ) if test_verilog else dut
  dut.elaborate()

  # Define input and output functions to the test vector simulator
  def tv_in( dut, test_vector ):
    dut.in_.val.value = test_vector[0]
    dut.in_.msg.value = test_vector[2]
    dut.out.rdy.value = test_vector[4]

  def tv_out( dut, test_vector ):
    assert dut.in_.rdy == test_vector[1]
    assert dut.out.val == test_vector[3]
    if test_vector[5] != '?':
      assert dut.out.msg == test_vector[5]

  # Run the test
  sim = TestVectorSimulator( dut, test_vectors, tv_in, tv_out )
  sim.run_test()

#=======================================================================
# Directed tests 
#=======================================================================
def test_2entry( dump_vcd, test_verilog ):
  """
  Test input unit implemented with 2-entry
  """
  run_iu_test( dump_vcd, test_verilog, InputUnit, 2, 16, [
    # Enqueue one element and then dequeue it
    # enq_val enq_rdy enq_bits deq_val deq_rdy deq_bits
    [ 1,      1,      0x0001,  0,      1,      '?'    ],
    [ 0,      1,      0x0000,  1,      1,      0x0001 ],
    [ 0,      1,      0x0000,  0,      0,      '?'    ],

    # Fill in the queue and enq/deq at the same time
    # enq_val enq_rdy enq_bits deq_val deq_rdy deq_bits
    [ 1,      1,      0x0002,  0,      0,      '?'    ],
    [ 1,      1,      0x0003,  1,      0,      0x0002 ],
    [ 0,      0,      0x0003,  1,      0,      0x0002 ],
    [ 1,      0,      0x0003,  1,      0,      0x0002 ],
    [ 1,      0,      0x0003,  1,      1,      0x0002 ],
    [ 1,      1,      0x0004,  1,      0,      '?'    ],
    [ 1,      0,      0x0004,  1,      1,      0x0003 ],
    [ 1,      1,      0x0005,  1,      0,      '?'    ],
    [ 0,      0,      0x0005,  1,      1,      0x0004 ],
    [ 0,      1,      0x0005,  1,      1,      0x0005 ],
    [ 0,      1,      0x0005,  0,      1,      '?'    ],
  ])
