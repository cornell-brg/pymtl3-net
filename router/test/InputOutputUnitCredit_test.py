"""
==========================================================================
InputOutputUnitCredit_test.py
==========================================================================
Composition test for input/output unit with credit based interfaces.

Author : Yanghui Ou
  Date : June 22, 2019
"""
from pymtl3                       import *
from pymtl3.stdlib.test.test_srcs import TestSrcRTL
from pymtl3.stdlib.rtl.queues     import BypassQueueRTL
from ocn_pclib.test.net_sinks     import TestNetSinkRTL
from ocn_pclib.ifcs.packets       import mk_generic_pkt
from ocn_pclib.ifcs.CreditIfc     import RecvRTL2CreditSendRTL, CreditRecvRTL2SendRTL
from ..InputUnitCreditRTL         import InputUnitCreditRTL
from ..SwitchUnitRTL              import SwitchUnitRTL
from ..OutputUnitCreditRTL        import OutputUnitCreditRTL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):
  def construct( s, Type, src_msgs, sink_msgs, vc=2, credit_line=2 ):

    s.src   = TestSrcRTL( Type, src_msgs )
    s.src_q = BypassQueueRTL( Type, num_entries=1 )
    s.output_unit = OutputUnitCreditRTL( Type, vc=vc, credit_line=credit_line )
    s.input_unit  = InputUnitCreditRTL( Type, vc=vc, credit_line=credit_line )
    s.switch_unit = SwitchUnitRTL( Type, num_inports=vc )
    s.sink = TestNetSinkRTL( Type, sink_msgs )

    s.src.send             //= s.src_q.enq
    s.src_q.deq            //= s.output_unit.get
    s.output_unit.send     //= s.input_unit.recv
    s.switch_unit.give.msg //= s.sink.recv.msg
    for i in range( vc ):
      s.input_unit.give[i] //= s.switch_unit.get[i]

    @s.update
    def up_sink_recv():
      s.sink.recv.en = s.switch_unit.give.rdy & s.sink.recv.rdy
      s.switch_unit.give.en = s.switch_unit.give.rdy & s.sink.recv.rdy

  def line_trace( s ):
    return "{} >>> {} >>> {} >>> {} >>> {}".format(
      s.src.line_trace(),
      s.output_unit.line_trace(),
      s.input_unit.line_trace(),
      s.switch_unit.line_trace(),
      s.sink.line_trace()
    )

  def done( s ):
    return s.src.done() and s.sink.done()

  def run_sim( s, max_cycles=1000 ):
    # Run simulation
    print("")
    ncycles = 0
    s.sim_reset()
    print("{:3}: {}".format( ncycles, s.line_trace() ))
    while not s.done() and ncycles < max_cycles:
      s.tick()
      ncycles += 1
      print("{:3}: {}".format( ncycles, s.line_trace() ))

    # Check timeout
    assert ncycles < max_cycles

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

def test_simple():
  Pkt = mk_generic_pkt( vc=2 )
  msgs = [
    Pkt( 0, 1, 0x04, 0, 0xdeadbabe ),
    Pkt( 0, 2, 0x02, 1, 0xfaceb00c ),
    Pkt( 0, 3, 0x03, 0, 0xdeadface ),
  ]
  th = TestHarness( Pkt, msgs, msgs )
  th.elaborate()
  th.apply( SimulationPass )
  th.sim_reset()
  th.run_sim()

def test_backpresure():
  Pkt = mk_generic_pkt( vc=2 )
  msgs = [
      # src dst opq vc_id payload
    Pkt( 0, 1, 0x04, 0, 0xdeadbabe ),
    Pkt( 0, 2, 0x02, 1, 0xfaceb00c ),
    Pkt( 0, 3, 0x03, 0, 0xdeadface ),
    Pkt( 0, 3, 0x03, 1, 0xdeadface ),
    Pkt( 0, 3, 0x03, 1, 0xdeadface ),
    Pkt( 0, 3, 0x03, 0, 0xdeadface ),
    Pkt( 0, 3, 0x03, 0, 0xdeadface ),
  ]
  th = TestHarness( Pkt, msgs, msgs )
  th.set_param( "top.sink.construct", initial_delay=20 )
  th.elaborate()
  th.apply( SimulationPass )
  th.sim_reset()
  th.run_sim()
