#=========================================================================
#SwitchUnitRTL_test.py
#=========================================================================
# Test for SwitchUnitRTL
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 1, 2019

import pytest

from pymtl import *
from pclib.rtl.valrdy_queues import PipeQueue1RTL, BypassQueue1RTL
from pclib.rtl.TestSource import TestSourceValRdy
from pclib.rtl.TestSink   import TestSinkValRdy
from pclib.ifcs import InValRdyIfc, OutValRdyIfc
from pclib.ifcs.EnRdyIfc import InEnRdyIfc, OutEnRdyIfc
from pclib.test import mk_test_case_table
from pymtl.passes.PassGroups import SimpleSim

from src.router.SwitchUnitRTL import SwitchUnitRTL
from ocn_pclib.enrdy_adapters import ValRdy2EnRdy, EnRdy2ValRdy

from pclib.rtl  import NormalQueueRTL
from pclib.rtl  import BypassQueue1RTL

#TODO: need check........








#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( RTLComponent ):

  def construct( s, MsgType, recv_en, recv_msgs, send_msgs, send_rdy ):

    s.switch_unit = SwitchUnitRTL ( MsgType  )

#  def done( s ):
#    return s.src.done() and s.sink.done()

  def line_trace( s ):
#    return s.src.line_trace() + "-> | " + s.input_unit.line_trace() + \
#                               " | -> " + s.sink.line_trace()
    return s.switch_unit.line_trace()

#-------------------------------------------------------------------------
# run_rtl_sim
#-------------------------------------------------------------------------

def run_rtl_sim( test_harness, max_cycles=10 ):

  test_harness.apply( SimpleSim )


  # Run simulation

  ncycles = 0
  print ""
  print "{}:{}".format( ncycles, test_harness.line_trace() )
  while ncycles < max_cycles:
    test_harness.tick()
    ncycles += 1
    print "{}:{}".format( ncycles, test_harness.line_trace() )

  # Check timeout

  assert ncycles < max_cycles

  test_harness.tick()
  test_harness.tick()
  test_harness.tick()

#-------------------------------------------------------------------------
# directed tests
#-------------------------------------------------------------------------

def basic_msgs():
  return [
    # en             msg      send_rdy    send_msg 
   [[0,0,0,0,0], [5,6,7,8,9],    0,          '?'   ],
   [[0,1,0,0,0], [1,2,3,4,5],    1,           2    ],
   [[0,1,1,1,0], [9,8,7,6,5],    0,           7    ],
   [[0,1,1,1,0], [9,8,7,6,5],    1,           7    ],
   [[0,1,1,1,0], [5,4,3,2,1],    1,           2    ],
   [[1,0,0,0,1], [3,4,5,6,7],    1,           7    ],
   [[0,1,1,0,1], [3,4,5,6,7],    1,           4    ],
  ]


#-------------------------------------------------------------------------
# directed tests
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  ( "          msg_func " ),
  [ "basic",  basic_msgs  ]
])

#-------------------------------------------------------------------------
# mk_test_msgs
#-------------------------------------------------------------------------

def mk_test_msgs( msg_list ):

  recv_en  = []
  recv_msgs = []

  for m in msg_list:
    recv_en.append  ( m[0] )
    recv_msgs.append( m[1] )
    send_msgs.append( m[2] )
    send_rdy.append ( m[3] )

  return ( recv_en, recv_msgs, send_msgs, send_rdy )

@pytest.mark.parametrize( **test_case_table )
def test( test_params ):

  msgs = test_params.msg_func()
  recv_en, recv_msgs, send_msgs, send_rdy = mk_test_msgs( msgs )

  print ""
  run_rtl_sim(
    TestHarness( Bits16, recv_en, recv_msgs, send_msg, send_rdy)
  )


def run_test( model, test_vectors ):
 
  model.elaborate()

  def tv_in( model, test_vector ):
    model.out.rdy.value = test_vector[2]
    for i in range( model.num_inports ):
      model.recv[i].en  = test_vector[0][i]
      model.recv[i].msg = test_vector[1][i]

  def tv_out( model, test_vector ):
    if test_vector[4] != '?':
      assert model.send.en == test_vector[3]
      if model.send.en == 1:      
        assert model.send.msg == test_vector[4]
  
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

def test_SwitchUnit( dump_vcd, test_verilog ):
  model = SwitchUnitRTL( Bits16, 5 )

  run_test( model, [
    # en             msg      send_rdy  send_en     send_msg 
   [[0,0,0,0,0], [5,6,7,8,9],    0,         0,         '?'   ],
   [[0,1,0,0,0], [1,2,3,4,5],    1,         1,          2    ],
   [[0,1,1,1,0], [9,8,7,6,5],    0,         1,          7    ],
   [[0,1,1,1,0], [9,8,7,6,5],    1,         1,          7    ],
   [[0,1,1,1,0], [5,4,3,2,1],    1,         1,          2    ],
   [[1,0,0,0,1], [3,4,5,6,7],    1,         1,          7    ],
   [[0,1,1,0,1], [3,4,5,6,7],    1,         1,          4    ],
  ])

#  run_test( model, [
#    # val_index   msg      out_rdy    out_val    out_msg 
#   [     1,        7,         0,         1,         '?'   ],
#   [     4,        9,         0,         1,          9    ],
#   [     2,        5,         0,         1,          5    ],
#   [     3,        2,         1,         1,          2    ],
#   [     0,        4,         1,         1,          4    ],
#  ])












