#=========================================================================
# InputUnitRTL_test.py
#=========================================================================
# Unit tests for InputUnitRTL.
# 
# Author : Yanghui Ou, Cheng Tan
#   date : Feb 14, 2019

from pymtl import *
from router.InputUnitRTL import InputUnitRTL
from pymtl.passes.PassGroups import SimpleSim
# from pclib.rtl.valrdy_queues_test import TestVectorSimulator

class TestVectorSimulator( object ):

  def __init__( self, model, test_vectors,
                set_inputs_func, verify_outputs_func, wait_cycles = 0 ):

    self.model               = model
    self.set_inputs_func     = set_inputs_func
    self.verify_outputs_func = verify_outputs_func
    self.test_vectors        = test_vectors
    self.wait_cycles         = wait_cycles

  def run_test( self ):

    # self.model.elaborate()
    self.model.apply( SimpleSim )

    print()
    for test_vector in self.test_vectors:

      # Set inputs
      self.set_inputs_func( self.model, test_vector )
      self.model.tick()

      # Print the line trace
      print self.model.line_trace()

      # Verify outputs
      self.verify_outputs_func( self.model, test_vector )
      

#-------------------------------------------------------------------------
# run_test_queue
#-------------------------------------------------------------------------
# Helper function that help run directed tests.

def run_test_queue( model, test_vectors ):
  
  # Define functions mapping the test vector to ports in model

  def tv_in( model, tv ):
    model.in_.val = tv[0]
    model.in_.msg = tv[2]
    model.out.rdy = tv[4]

  def tv_out( model, tv ):
    if tv[1] != '?': assert model.in_.rdy == tv[1]
    if tv[3] != '?': assert model.out.val == tv[3]
    if tv[5] != '?': assert model.out.msg == tv[5]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

#-------------------------------------------------------------------------
# directed tests 
#-------------------------------------------------------------------------

def test_compile():
  _ = InputUnitRTL( num_entries=1, pkt_type=Bits32 ) 

def test_32bits():
  B1  = mk_bits(1)
  B32 = mk_bits(32)
  run_test_queue( InputUnitRTL( 1, Bits32 ), [
    # enq.val enq.rdy enq.msg  deq.val deq.rdy deq.msg
    [  B1(1) , B1(1) ,B32(123), B1(0) , B1(1) ,  '?'    ],
    [  B1(1) , B1(0) ,B32(345), B1(1) , B1(0) ,B32(123) ],
    [  B1(1) , B1(0) ,B32(567), B1(1) , B1(0) ,B32(123) ],
    [  B1(1) , B1(0) ,B32(567), B1(1) , B1(1) ,B32(123) ],
    [  B1(1) , B1(1) ,B32(567), B1(0) , B1(1) ,B32(123) ],
    [  B1(0) , B1(0) ,B32(0  ), B1(1) , B1(1) ,B32(567) ],
    [  B1(0) , B1(1) ,B32(0  ), B1(0) , B1(0) ,  '?'    ],
  ] )
