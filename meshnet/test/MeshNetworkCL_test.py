"""
==========================================================================
MeshNetworkCL_test.py
==========================================================================
Test for NetworkCL

Author : Yanghui Ou
  Date : May 19, 2019
"""
import pytest
from pymtl3                    import *
from pymtl3.stdlib.test               import mk_test_case_table
from pymtl3.stdlib.test.test_srcs     import TestSrcCL
from ocn_pclib.test.net_sinks import TestNetSinkCL
from ocn_pclib.ifcs.packets   import mk_mesh_pkt
from ocn_pclib.ifcs.positions import mk_mesh_pos
from meshnet.MeshNetworkCL    import MeshNetworkCL
from router.InputUnitCL       import InputUnitCL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, PktType, mesh_wid, mesh_ht,
                 src_msgs, sink_msgs,
                 src_initial, src_interval,
                 sink_initial, sink_interval ):

    s.nrouters = mesh_wid * mesh_ht

    MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )
    match_func = lambda a, b : a==b
    s.dut = MeshNetworkCL( PktType, MeshPos, mesh_wid, mesh_ht, 0 )

    s.srcs  = [ TestSrcCL( PktType, src_msgs[i],  src_initial,  src_interval  )
                for i in range( s.nrouters ) ]
    s.sinks = [ TestNetSinkCL( PktType, sink_msgs[i], sink_initial, sink_interval, match_func=match_func)
                for i in range( s.nrouters ) ]

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
  test_harness.elaborate()

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

def mk_src_sink_msgs( pkts, mesh_wid, mesh_ht ):
  nrouters = mesh_wid * mesh_ht
  src_msgs  = [ [] for _ in range( nrouters ) ]
  sink_msgs = [ [] for _ in range( nrouters ) ]

  for pkt in pkts:
    src_id  = pkt.src_y * mesh_wid + pkt.src_x
    sink_id = pkt.dst_y * mesh_wid + pkt.dst_x
    src_msgs [ src_id ].append( pkt )
    sink_msgs[ sink_id ].append( pkt )

  return src_msgs, sink_msgs

def mk_pkt_list( PktType, lst ):
  ret = []
  for m in lst:
    src_x, src_y, dst_x, dst_y, opq, payload = m[0], m[1], m[2], m[3], m[4], m[5]
    ret.append( PktType( src_x, src_y, dst_x, dst_y, opq, payload ) )
  return ret

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

def simple_msg( PktType, mesh_wid=2, mesh_ht=2 ):
  return mk_pkt_list( PktType, [
  #   src_x src_y dst_x dst_y opq   payload
    ( 0,    0,    0,    1,    0x00, 0x0010  ),
    ( 1,    0,    1,    1,    0x01, 0x0020  ),
  ])

def simple_4x4( PktType, mesh_wid=2, mesh_ht=2 ):
  return mk_pkt_list( PktType, [
  #   src_x src_y dst_x dst_y opq   payload
    ( 0,    0,    0,    1,    0x00, 0x0010  ),
    ( 1,    0,    1,    1,    0x01, 0x0020  ),
    ( 3,    2,    1,    1,    0x02, 0x0020  ),
    ( 1,    0,    1,    1,    0x03, 0x0020  ),
    ( 1,    3,    2,    1,    0x04, 0x0020  ),
    ( 3,    3,    1,    0,    0x05, 0x0020  ),
  ])

def simple_8x8( PktType, mesh_wid=2, mesh_ht=2 ):
  return mk_pkt_list( PktType, [
  #   src_x src_y dst_x dst_y opq   payload
    ( 0,    0,    0,    1,    0x00, 0x0010  ),
    ( 1,    0,    1,    1,    0x01, 0x0020  ),
    ( 3,    2,    1,    1,    0x02, 0x0020  ),
    ( 1,    0,    1,    1,    0x03, 0x0020  ),
    ( 1,    3,    2,    1,    0x04, 0x0020  ),
    ( 3,    5,    1,    0,    0x05, 0x0020  ),
  ])
#-------------------------------------------------------------------------
# test case table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (            "msg_func    wid  ht  src_init src_intv sink_init sink_intv"),
  ["simle2x2", simple_msg, 2,   2,  0,       0,       0,        0         ],
  ["simle4x4", simple_4x4, 4,   4,  0,       0,       0,        0         ],
  ["simle8x8", simple_8x8, 8,   8,  0,       0,       0,        0         ],
])

#-------------------------------------------------------------------------
# run test
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_mesh_simple( test_params ):
  PktType = mk_mesh_pkt(
    mesh_wid=test_params.wid,
    mesh_ht =test_params.ht,
    nvcs=1,
  )
  pkt_list = test_params.msg_func( PktType, test_params.wid, test_params.ht )
  src_msgs, sink_msgs = mk_src_sink_msgs( pkt_list, test_params.wid, test_params.ht )
  th = TestHarness(
    PktType,
    test_params.wid,
    test_params.ht,
    src_msgs,
    sink_msgs,
    test_params.src_init,
    test_params.src_intv,
    test_params.sink_init,
    test_params.sink_intv,
  )
  run_sim( th )
