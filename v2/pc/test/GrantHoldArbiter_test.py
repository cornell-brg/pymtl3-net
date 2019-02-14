import tempfile
from pymtl                import *
from pclib.test           import TestVectorSimulator
from pc.GrantHoldArbiter import GrantHoldArbiter
from hypothesis.stateful import * 
from hypothesis import strategies as st

def run_test( model, test_vectors ):
 
  model.elaborate()

  def tv_in( model, test_vector ):
    model.reqs.value = test_vector[0]
    model.hold.value = test_vector[1]

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
#-----------------------------------------------------------------------
# Hypothesis stateful testing
#-----------------------------------------------------------------------
# An reference model in pure python
class ArbiterFL:
  def __init__( self, nreqs ):
    self.priority   = Bits( nreqs, 1 )
    self.last       = Bits( nreqs, 0 )
    self.nreqs      = nreqs
    self.reqs_reg   = Bits( nreqs, 0 )
    self.hold_reg   = Bits(     1, 0 )
    self.grants_reg = Bits( nreqs, 0 ) 
  
  def set_reqs( self, reqs ):
    self.reqs_reg.value = reqs 

  def set_hold( self, hold ):
    self.hold_reg.value = hold 

  def eval( self ):
    if self.hold_reg:
      return self.last
    else:
      reqs  = self.reqs_reg
      grant = Bits( self.nreqs, 0    )
      
      # find the one with highest priority
      for i in range( self.nreqs ):
        if self.priority[i]:
          p_idx = i

      idx = p_idx
      for _ in range( self.nreqs ):
        if reqs[idx]: 
          grant[idx] = 1
          break
        idx = ( idx + 1 ) % self.nreqs
      self.grants_reg.value = grant 

  def tick( self ):
    if not self.hold_reg:
      reqs  = self.reqs_reg 
      
      # find the one with highest priority
      for i in range( self.nreqs ):
        if self.priority[i]:
          p_idx = i

      idx = p_idx
      for _ in range( self.nreqs ):
        if reqs[idx]: 
          # update priority
          self.priority.value = 0 
          if idx != self.nreqs - 1:
            self.priority[idx+1] = 1
          else:
            self.priority[0] = 1
          break
        idx = ( idx + 1 ) % self.nreqs
    self.last = self.grants_reg

  def request( self, reqs, hold ):
    self.set_reqs( reqs )
    self.set_hold( hold )
    self.eval()
    self.tick()
    return self.grants_reg


class ArbiterComparison( RuleBasedStateMachine ):
  num_ports = 0 
  def __init__( self ):
    super( ArbiterComparison, self ).__init__()
    self.tempd = tempfile.mktemp()
    nreqs = 5 
    # TODO: parametrize nreqs
    num_ports    = nreqs
    self.arb_ref = ArbiterFL( nreqs  )
    self.arb_dut = GrantHoldArbiter( nreqs )
    self.arb_dut.elaborate()
    self.dut_sim = SimulationTool( self.arb_dut )
    self.dut_sim.reset()

    self.request_called = False 
    self.eval_called    = False 
    print "="*72
  # Send a pulse to set the request
  @precondition( lambda self: not self.request_called )
  @rule( reqs = st.integers( 0, 31 ), 
         hold = st.integers( 0, 1 ) )
  def set_req( self, reqs, hold ):
    self.arb_ref.set_reqs( reqs )
    self.arb_ref.set_hold( hold )
    
    self.arb_dut.reqs.value = reqs
    self.arb_dut.hold.value = hold
    self.request_called = True
    # print "request_called set to True"

  @precondition( lambda self: not self.eval_called and self.request_called ) 
  @rule()
  def eval_and_check( self ):
    self.arb_ref.eval()

    self.dut_sim.eval_combinational()
    self.dut_sim.print_line_trace()
    self.eval_called = True 
    assert self.arb_ref.grants_reg == self.arb_dut.grants
  
  @precondition( lambda self: self.eval_called )
  @rule()
  def tick( self ):
    self.arb_ref.tick()
    self.arb_ref.set_reqs( 0 )
    self.arb_ref.set_hold( 0 )

    self.dut_sim.cycle()
    self.arb_dut.reqs.value = 0
    self.arb_dut.hold.value = 0
    
    self.request_called = False
    self.eval_called    = False

def test_hypothesis_stateful():
  # TODO: Figure out why [TestCase] does nothing. 
  # TestArbiterComparison = ArbiterComparison.TestCase
  run_state_machine_as_test( ArbiterComparison )

# Directed test to verify the reference model
def test_arb_fl():
  arb = ArbiterFL( 4 )
                    # reqs    hold   grants   priority
  assert arb.request( 0b0000, 0 ) == 0b0000 # 0001
  assert arb.request( 0b1000, 0 ) == 0b1000 # 0001
  assert arb.request( 0b1100, 0 ) == 0b0100 # 0100  
  assert arb.request( 0b1100, 0 ) == 0b1000 # 1000
  assert arb.request( 0b0000, 1 ) == 0b1000 # 1000
  assert arb.request( 0b0111, 0 ) == 0b0001 # 1000
  assert arb.request( 0b1111, 0 ) == 0b0010 # 0010
  assert arb.request( 0b1111, 1 ) == 0b0010 # 0010
  assert arb.request( 0b1111, 1 ) == 0b0010 # 0010
