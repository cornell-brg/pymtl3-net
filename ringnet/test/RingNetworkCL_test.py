#=========================================================================
# MeshNetworkRTL_test.py
#=========================================================================
# Test for NetworkRTL
#
# Author : Yanghui Ou
#   Date : May 19, 2019

import pytest
from pymtl                   import *
from pclib.test              import mk_test_case_table
from pclib.test.test_srcs    import TestSrcCL
from pclib.test.test_sinks   import TestSinkCL
from ocn_pclib.ifcs.Packet   import BasePacket, mk_base_pkt
from ocn_pclib.ifcs.Position import RingPosition, mk_ring_pos
from ringnet.RingNetworkCL   import RingNetworkCL
from router.InputUnitCL      import InputUnitCL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, PktType, nrouters, 
                 src_msgs, sink_msgs, 
                 src_initial, src_interval, 
                 sink_initial, sink_interval ):

    s.nrouters = nrouters

    RingPos = mk_ring_pos( s.nrouters )
    s.dut = RingNetworkCL( PktType, RingPos, s.nrouters, 0 )

    s.srcs  = [ TestSrcCL ( src_msgs[i],  src_initial,  src_interval  )
                for i in range ( s.nrouters ) ]
    s.sinks = [ TestSinkCL( sink_msgs[i], sink_initial, sink_interval) 
                for i in range ( s.nrouters ) ]

    # Connections
    for i in range ( s.nrouters ):
      s.connect( s.srcs[i].send, s.dut.recv[i]   )
      s.connect( s.dut.send[i],  s.sinks[i].recv )

  def done( s ):
    srcs_done = 1
    sinks_done = 1
    for i in range( s.nrouters ):
      if s.srcs[i].done() == 0:
        srcs_done = 0
    for i in range( s.nrouters ):
      if s.sinks[i].done() == 0:
        sinks_done = 0
    return srcs_done and sinks_done

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
  print "{:2}:{}".format( ncycles, test_harness.line_trace() )
  while not test_harness.done() and ncycles < max_cycles:
    test_harness.tick()
    ncycles += 1
    print "{:2}:{}".format( ncycles, test_harness.line_trace() )

  # Check timeout

  assert ncycles < max_cycles

  test_harness.tick()
  test_harness.tick()
  test_harness.tick()

#-------------------------------------------------------------------------
# Helper functions
#-------------------------------------------------------------------------

def mk_src_sink_msgs( pkts, nrouters ):
  src_msgs  = [ [] for _ in range( nrouters ) ]
  sink_msgs = [ [] for _ in range( nrouters ) ]
  
  for pkt in pkts:
    src_id  = pkt.src
    sink_id = pkt.dst
    src_msgs[ src_id ].append( pkt )
    sink_msgs[ sink_id ].append( pkt )

  return src_msgs, sink_msgs

def mk_pkt_list( lst ):
  ret = []
  for m in lst:
    src, dst, opq, payload = m[0], m[1], m[2], m[3]
    ret.append( mk_base_pkt( src, dst, opq, payload ) )
  return ret

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

def simple_msg( nrouters=4 ):
  return mk_pkt_list( [
  #   src dst opq   payload
    ( 0,  1,  0x00, 0x0010  ),
    ( 1,  2,  0x01, 0x0020  ),
  ])

#-------------------------------------------------------------------------
# test case table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (            "msg_func    nrouters src_init src_intv sink_init sink_intv"),
  ["simle_msg", simple_msg, 4,       0,       0,       0,        0         ],
])

#-------------------------------------------------------------------------
# run test
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_ring_simple( test_params ):
  pkt_list = test_params.msg_func( test_params.nrouters )
  src_msgs, sink_msgs = mk_src_sink_msgs( pkt_list, test_params.nrouters )
  th = TestHarness( 
    BasePacket, 
    test_params.nrouters,
    src_msgs,
    sink_msgs, 
    test_params.src_init,
    test_params.src_intv,
    test_params.sink_init,
    test_params.sink_intv,
  )
  run_sim( th )
