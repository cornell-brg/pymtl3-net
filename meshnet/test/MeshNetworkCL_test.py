"""
==========================================================================
MeshNetworkCL_test.py
==========================================================================
Test for NetworkCL

Author : Yanghui Ou
  Date : May 19, 2019
"""
import pytest

from meshnet.MeshNetworkCL import MeshNetworkCL
from ocnlib.ifcs.packets import mk_mesh_pkt
from ocnlib.ifcs.positions import mk_mesh_pos
from ocnlib.utils import run_sim
from ocnlib.test.net_sinks import TestNetSinkCL
from pymtl3 import *
from pymtl3.stdlib.test import mk_test_case_table
from pymtl3.stdlib.test.test_srcs import TestSrcCL
from router.InputUnitCL import InputUnitCL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, PktType, ncols, nrows,
                 src_msgs, sink_msgs,
                 src_initial, src_interval,
                 sink_initial, sink_interval ):

    s.nrouters = ncols * nrows

    MeshPos = mk_mesh_pos( ncols, nrows )
    match_func = lambda a, b : a==b
    s.dut = MeshNetworkCL( PktType, MeshPos, ncols, nrows, 0 )

    s.srcs  = [ TestSrcCL( PktType, src_msgs[i],  src_initial,  src_interval  )
                for i in range( s.nrouters ) ]
    s.sinks = [ TestNetSinkCL( PktType, sink_msgs[i], sink_initial, sink_interval, match_func=match_func)
                for i in range( s.nrouters ) ]

    # Connections
    for i in range ( s.nrouters ):
      s.srcs[i].send //= s.dut.recv[i]
      s.dut.send[i]  //= s.sinks[i].recv

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
# Helper functions
#-------------------------------------------------------------------------

def mk_src_sink_msgs( PktType, msgs, ncols, nrows ):
  nrouters = ncols * nrows
  src_msgs  = [ [] for _ in range( nrouters ) ]
  sink_msgs = [ [] for _ in range( nrouters ) ]

  for msg in msgs:
    src_x, src_y, dst_x, dst_y, opq, payload = msg
    src_id  = src_y * ncols + src_x
    sink_id = dst_y * ncols + dst_x

    src_msgs [ src_id ] .append( PktType(*msg) )
    sink_msgs[ sink_id ].append( PktType(*msg) )

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

simple_2x2 = [
#   src_x src_y dst_x dst_y opq   payload
  ( 0,    0,    0,    1,    0x00, 0x0010  ),
  ( 1,    0,    1,    1,    0x01, 0x0020  ),
]

simple_4x4 = [
#   src_x src_y dst_x dst_y opq   payload
  ( 0,    0,    0,    1,    0x00, 0x0010  ),
  ( 1,    0,    1,    1,    0x01, 0x0020  ),
  ( 3,    2,    1,    1,    0x02, 0x0020  ),
  ( 1,    0,    1,    1,    0x03, 0x0020  ),
  ( 1,    3,    2,    1,    0x04, 0x0020  ),
  ( 3,    3,    1,    0,    0x05, 0x0020  ),
]

simple_8x8 = [
#   src_x src_y dst_x dst_y opq   payload
  ( 0,    0,    0,    1,    0x00, 0x0010  ),
  ( 1,    0,    1,    1,    0x01, 0x0020  ),
  ( 3,    2,    1,    1,    0x02, 0x0020  ),
  ( 1,    0,    1,    1,    0x03, 0x0020  ),
  ( 1,    3,    2,    1,    0x04, 0x0020  ),
  ( 3,    5,    1,    0,    0x05, 0x0020  ),
]

#-------------------------------------------------------------------------
# test case table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (            "msg_list    wid  ht  src_init src_intv sink_init sink_intv"),
  ["simple2x2", simple_2x2, 2,   2,  0,       0,       0,        0         ],
  ["simple4x4", simple_4x4, 4,   4,  0,       0,       0,        0         ],
  ["simple8x8", simple_8x8, 8,   8,  0,       0,       0,        0         ],
])

#-------------------------------------------------------------------------
# run test
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_mesh_simple( test_params ):
  PktType = mk_mesh_pkt( ncols=test_params.wid,
                         nrows=test_params.ht, vc=1 )

  src_msgs, sink_msgs = mk_src_sink_msgs( PktType, test_params.msg_list,
                                          test_params.wid, test_params.ht )
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
