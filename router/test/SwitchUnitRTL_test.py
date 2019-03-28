#=========================================================================
# SwitchUnitRTL_test.py
#=========================================================================
# Test for SwitchUnitRTL
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 1, 2019

import tempfile
from pymtl                   import *
from pclib.test              import TestVectorSimulator
from ocn_pclib.ifcs.Packet   import Packet, mk_pkt
from router.SwitchUnitRTL    import SwitchUnitRTL

from pymtl.passes.PassGroups import SimpleSim
from pclib.test.test_srcs    import TestSrcRTL
from pclib.test.test_sinks   import TestSinkRTL

#-------------------------------------------------------------------------
# Vector-based test for switch unit with get/send interface 
#-------------------------------------------------------------------------

def run_test_get_send( model, test_vectors ):

  def tv_in( model, test_vector ):

    for i in range( model.num_inports ):
      model.get[i].rdy = test_vector[0][i]
      pkt = mk_pkt( 0, 0, 1, 1, i, test_vector[1][i])
      model.get[i].msg = pkt

    model.send.rdy = test_vector[3]

  def tv_out( model, test_vector ):
    for i in range( model.num_inports ):
      assert model.get[i].en == test_vector[2][i]

    assert model.send.en == test_vector[4]
    if model.send.en == 1:
      assert model.send.msg.payload == test_vector[5]
  
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

vector_msgs = [
  #  get.rdy     get.msg       get.en     send.rdy send.en send.msg
  [ [1,0,0,0,0], [5,6,7,8,9],  [0,0,0,0,0],     0,       0,     5    ],
  [ [1,0,0,0,0], [6,7,8,9,5],  [1,0,0,0,0],     1,       1,     6    ],
  [ [1,1,0,0,0], [0,1,2,3,4],  [0,1,0,0,0],     1,       1,     1    ],
  [ [0,1,0,0,0], [1,2,3,4,5],  [0,1,0,0,0],     1,       1,     2    ],
  [ [0,1,1,1,0], [9,8,7,6,5],  [0,0,1,0,0],     1,       1,     7    ],
  [ [0,1,1,1,0], [8,7,6,5,4],  [0,0,0,1,0],     1,       1,     5    ],
  [ [0,1,1,1,0], [7,6,5,4,3],  [0,0,0,0,0],     0,       0,     0    ],
  [ [0,1,1,1,0], [8,7,6,5,4],  [0,1,0,0,0],     1,       1,     7    ],
  [ [0,1,1,1,0], [9,8,7,6,5],  [0,0,1,0,0],     1,       1,     7    ],
  [ [1,1,1,1,1], [5,4,3,2,1],  [0,0,0,1,0],     1,       1,     2    ],
  [ [1,1,1,1,1], [5,4,3,2,1],  [0,0,0,0,1],     1,       1,     1    ],
  [ [1,1,1,1,1], [5,4,3,2,1],  [1,0,0,0,0],     1,       1,     5    ],
]

def test_get_send( dump_vcd, test_verilog ):

  model = SwitchUnitRTL( Packet )
  run_test_get_send( model, vector_msgs )


#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( ComponentLevel6 ):

  def construct( s, MsgType, src_msgs, sink_msgs, src_initial,
                 src_interval, sink_initial, sink_interval,
                 arrival_time=None ):

    s.dut  = SwitchUnitRTL( MsgType )

    s.srcs = [ TestSrcRTL ( MsgType, src_msgs[i],  src_initial,  src_interval )
             for i in range ( s.dut.num_inports ) ]
    s.sink = TestSinkRTL ( MsgType, sink_msgs, sink_initial, 
             sink_interval, arrival_time )

    # Connections
    s.connect( s.dut.send, s.sink.recv )
    for i in range ( s.dut.num_inports ):
      s.connect( s.srcs[i].send.msg, s.dut.get[i].msg )
#      s.connect( s.srcs[i].send.rdy, s.dut.get[i].rdy )

    @s.update
    def up_dut_rdy():
      for i in range (s.dut.num_inports):
#        if s.sink.recv.rdy:
#        s.srcs[i].send.rdy = s.sink.recv.rdy
#        s.dut.get[i].rdy   = s.sink.recv.rdy
        s.srcs[i].send.rdy = 1
        s.dut.get[i].rdy   = 1


  def done( s ):
    return s.sink.done()

  def line_trace( s ):
    return s.dut.line_trace()

#-------------------------------------------------------------------------
# run_rtl_sim
#-------------------------------------------------------------------------

def run_sim( test_harness, max_cycles=100 ):

  # Create a simulator

  test_harness.apply( SimpleSim )
  test_harness.sim_reset()


  # Run simulation

  ncycles = 0
  print ""
  print "{}:{}".format( ncycles, test_harness.line_trace() )
  while not test_harness.done() and ncycles < max_cycles:
    test_harness.tick()
    ncycles += 1
    print "{}:{}".format( ncycles, test_harness.line_trace() )

  # Check timeout

  assert ncycles < max_cycles

#  test_harness.tick()
#  test_harness.tick()
#  test_harness.tick()

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

def test_normal_simple():
  src_msgs  = [
    [11,12],
    [21,22],
    [31,32],
    [41,42],
    [51,52]
  ]
  sink_msgs = [ 11,22,32,42,52 ]
 
  arrival_pipe = [ 1,2,3,4,5 ]

  th = TestHarness( Bits16, src_msgs, sink_msgs, 0, 0, 0, 0,
                    arrival_pipe )
  run_sim( th )
