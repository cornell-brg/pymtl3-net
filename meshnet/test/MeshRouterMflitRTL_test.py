'''
==========================================================================
MeshRouterMflitRTL_test.py
==========================================================================
Test cases for mesh router that supports multi-flit packet.

Author : Yanghui Ou
  Date : Feb 13, 2020
'''
import pytest
from pymtl3 import *
from pymtl3.stdlib.test import mk_test_case_table
from ocnlib.utils import to_bitstruct
from ocnlib.packets import MflitPacket as Packet
from ocnlib.test import run_sim
from ocnlib.test.test_srcs import MflitPacketSourceRTL as TestSource
from ocnlib.test.test_sinks import MflitPacketSinkRTL as TestSink

from ..MeshRouterFL import MeshRouterMflitFL
from ..MeshRouterMflitRTL import MeshRouterMflitRTL

#-------------------------------------------------------------------------
# bitstructs for testing
#-------------------------------------------------------------------------

@bitstruct
class TestHeader:
  opaque : Bits12
  src_x  : Bits4
  src_y  : Bits4
  dst_x  : Bits4
  dst_y  : Bits4
  plen   : Bits4

@bitstruct
class TestPosition:
  pos_x : Bits4
  pos_y : Bits4

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, Header, Position, pos_x, pos_y, src_pkts, sink_pkts ):
    nports = 5

    s.src  = [ TestSource( Header, src_pkts[i] ) for i in range( nports ) ]
    s.dut  = MeshRouterMflitRTL( Header, Position )
    s.sink = [ TestSink( Header, sink_pkts[i] ) for i in range( nports ) ]

    for i in range( nports ):
      s.src[i].send //= s.dut.recv[i]
      s.dut.send[i] //= s.sink[i].recv

    s.dut.pos //= Position( pos_x, pos_y )

  def done( s ):
    src_done = True
    sink_done = True
    for m in s.src:
      src_done &= m.done()
    for m in s.sink:
      sink_done &= m.done()
    return src_done and sink_done

  def line_trace( s ):
    return s.dut.line_trace()

#-------------------------------------------------------------------------
# mk_pkt
#-------------------------------------------------------------------------

def mk_pkt( src_x, src_y, dst_x, dst_y, payload=[], opaque=0 ):
  plen        = len( payload )
  header      = TestHeader( opaque, src_x, src_y, dst_x, dst_y, plen )
  header_bits = to_bits( header )
  flits       = [ header_bits ] + payload
  return Packet( TestHeader, flits )

#-------------------------------------------------------------------------
# sanity check
#-------------------------------------------------------------------------

def test_sanity_check():
  dut = MeshRouterMflitRTL( TestHeader, TestPosition )
  dut.elaborate()
  dut.apply( SimulationPass() )
  dut.sim_reset()
  dut.tick()

#-------------------------------------------------------------------------
# test case: basic
#-------------------------------------------------------------------------

def basic_pkts( pos_x, pos_y ):
  return [
    #       src_x  y      dst_x  y      payload
    mk_pkt(     0, 0,     pos_x, pos_y, [ 0x8badf00d             ] ),
    mk_pkt( pos_x, pos_y, 0,     0,     [ 0x8badf00d, 0xdeadbeef ] ),
  ]

#-------------------------------------------------------------------------
# test case: hotspot
#-------------------------------------------------------------------------

def hotspot_pkts( pos_x, pos_y ):
  return [
    #       src_x  y      dst_x  y      payload
    mk_pkt(     0, 0,     pos_x, pos_y, [ 0x8badf00d                         ] ),
    mk_pkt(     0, 1,     pos_x, pos_y, [ 0x8badf00d, 0xdeadbeef             ] ),
    mk_pkt( pos_x, 0,     pos_x, pos_y, [                                    ] ),
    mk_pkt(     2, pos_y, pos_x, pos_y, [ 0xdeadbeef, 0xfaceb00c, 0xdeadfa11 ] ),
    mk_pkt(     2, pos_y, pos_x, pos_y, [                                    ] ),
    mk_pkt(     2, pos_y, pos_x, pos_y, [ 0xdeadc0de ] * 10                   ),
  ]

#-------------------------------------------------------------------------
# test case: long
#-------------------------------------------------------------------------

def long_pkts( pos_x, pos_y ):
  return [
    #       src_x  y      dst_x  y      payload
    mk_pkt(     0, 0,     pos_x, pos_y, [ 0x8badf00d                         ] * 13 ),
    mk_pkt(     0, 1,     pos_x, pos_y, [ 0x8badf00d, 0xdeadbeef             ] * 6  ),
    mk_pkt( pos_x, 0,     pos_x, pos_y, [                                    ]      ),
    mk_pkt(     2, 1,     pos_x, pos_y, [ 0xdeadbeef, 0xfaceb00c, 0xdeadfa11 ] * 3  ),
    mk_pkt(     7, pos_y, pos_x, pos_y, [                                    ]      ),
    mk_pkt(     0, 8,     pos_x, pos_y, [ 0xdeadc0de                         ] * 10 ),
  ]

#-------------------------------------------------------------------------
# test case table
#-------------------------------------------------------------------------

table = [
  (               'msg_func      pos_x  pos_y' ),
  [ 'basic',       basic_pkts,       1,     1  ],
  [ 'hotspot2_3',  hotspot_pkts,     2,     3  ],
  [ 'hotspot4_4',  hotspot_pkts,     4,     4  ],
  [ 'long_4_4',    long_pkts,        4,     4  ],
]

for x in range(4):
  for y in range(4):
    table.append([ f'hotspot_{x},{y}', hotspot_pkts, x, y ])

for x in range(4):
  for y in range(4):
    table.append([ f'long_{x},{y}', long_pkts, x, y ])

test_case_table = mk_test_case_table( table )

#-------------------------------------------------------------------------
# test driver
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_mflit_mesh_router( test_params ):
  ref  = MeshRouterMflitFL( TestHeader, test_params.pos_x, test_params.pos_y )
  pkts = test_params.msg_func( test_params.pos_x, test_params.pos_y )

  src_pkts = ref.arrange_src_pkts( pkts )
  dst_pkts = ref.route( src_pkts )

  th = TestHarness( TestHeader, TestPosition,
                    test_params.pos_x, test_params.pos_y,
                    src_pkts, dst_pkts )
  run_sim( th )
