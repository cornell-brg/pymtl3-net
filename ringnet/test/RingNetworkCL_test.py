#=========================================================================
# MeshNetworkRTL_test.py
#=========================================================================
# Test for NetworkRTL
#
# Author : Yanghui Ou
#   Date : May 19, 2019

import pytest

from pymtl3 import *
from pymtl3.stdlib.test import mk_test_case_table
from pymtl3.stdlib.test.test_srcs import TestSrcCL
from ocn_pclib.test.net_sinks import TestNetSinkCL
from ocn_pclib.ifcs.packets   import mk_ring_pkt
from ocn_pclib.ifcs.positions import mk_ring_pos
from ringnet.RingNetworkCL    import RingNetworkCL
from router.InputUnitCL       import InputUnitCL

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

    s.srcs  = [ TestSrcCL( src_msgs[i],  src_initial,  src_interval  )
                for i in range ( s.nrouters ) ]
    s.sinks = [ TestNetSinkCL( sink_msgs[i], sink_initial, sink_interval)
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

def mk_pkt_list( PktType, lst ):
  ret = []
  for m in lst:
    src, dst, opq, payload = m[0], m[1], m[2], m[3]
    ret.append( PktType( src, dst, opq, 0, payload ) )
  return ret

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

def simple_msg( PktType, nrouters=4 ):
  return mk_pkt_list( PktType, [
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
  PktType = mk_ring_pkt(
    nrouters=test_params.nrouters,
    nvcs=2,
  )
  pkt_list = test_params.msg_func( PktType, test_params.nrouters )
  src_msgs, sink_msgs = mk_src_sink_msgs( pkt_list, test_params.nrouters )
  th = TestHarness(
    PktType,
    test_params.nrouters,
    src_msgs,
    sink_msgs,
    test_params.src_init,
    test_params.src_intv,
    test_params.sink_init,
    test_params.sink_intv,
  )
  run_sim( th )