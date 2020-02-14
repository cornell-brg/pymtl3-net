'''
==========================================================================
MeshRouterMFlitRTL_test.py
==========================================================================
Test cases for mesh router that supports multi-flit packet.

Author : Yanghui Ou
  Date : Feb 13, 2020
'''
import pytest
from pymtl3 import *
from pymtl3.stdlib.test import mk_test_case_table
from ocnlib.utils import to_bitstruct
from ocnlib.packets import MultiFlitPacket as Packet
from ocnlib.test.test_srcs import MultiFlitPacketSourceRTL as TestSource
from ocnlib.test.test_sinks import MultiFlitPacketSinkRTL as TestSink

from ..MeshRouterFL import MeshRouterMFlitFL
from ..MeshRouterMFlitRTL import MeshRouterMFlitRTL

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
    s.dut  = MeshRouterMFlitRTL( Header, Position )
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
# run_sim
#-------------------------------------------------------------------------
# TODO: use stdlib run_sim omce pymtl3 is updated

def run_sim( th, max_cycles=200 ):
  th.elaborate()
  th.apply( SimulationPass() )
  print()
  th.sim_reset()

  ncycles = 0
  while not th.done() and ncycles < max_cycles:
    print( f'{ncycles:3}:{th.line_trace()}' )
    th.tick()
    ncycles += 1

  assert th.done()
  th.tick()
  th.tick()
  th.tick()

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
  dut = MeshRouterMFlitRTL( TestHeader, TestPosition )
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
# test case table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (          'msg_func    pos_x  pos_y' ),
  [ 'basic',  basic_pkts,     1,     1  ],
])

#-------------------------------------------------------------------------
# test driver
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_mflit_mesh_router( test_params ):
  ref  = MeshRouterMFlitFL( TestHeader, test_params.pos_x, test_params.pos_y )
  pkts = test_params.msg_func( test_params.pos_x, test_params.pos_y )

  src_pkts = ref.arrange_src_pkts( pkts )
  dst_pkts = ref.route( src_pkts )

  th = TestHarness( TestHeader, TestPosition,
                    test_params.pos_x, test_params.pos_y,
                    src_pkts, dst_pkts )
  run_sim( th )
