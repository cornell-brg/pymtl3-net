#=========================================================================
# TestVectorSimulator.py
#=========================================================================
# A test vector simulator.
#
# Author : Yanghui Ou
#   Date : Feb 18, 2019

from pymtl import *
from pymtl.passes.PassGroups import SimpleSim

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
