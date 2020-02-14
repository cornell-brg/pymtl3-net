'''
==========================================================================
MeshNetworkMFlitRTL_test.py
==========================================================================
Test cases for multi-flit mesh.

Author : Yanghui Ou
  Date : Feb 14, 2020
'''
import pytest
from pymtl3 import *
from pymtl3.stdlib.test import mk_test_case_table
from ocnlib.utils import to_bitstruct
from ocnlib.packets import MultiFlitPacket as Packet
from ocnlib.test.test_srcs import MultiFlitPacketSourceRTL as TestSource
from ocnlib.test.test_sinks import MultiFlitPacketSinkRTL as TestSink
from ..MeshNetworkMFlitRTL import MeshNetworkMFlitRTL

#-------------------------------------------------------------------------
# TestHeader
#-------------------------------------------------------------------------

@bitstruct
class TestHeader:
  opaque: Bits8
  src_x : Bits4
  src_y : Bits4
  dst_x : Bits4
  dst_y : Bits4
  plen  : Bits8

#-------------------------------------------------------------------------
# TestPosition
#-------------------------------------------------------------------------

@bitstruct
class TestPosition:
  pos_x : Bits4
  pos_y : Bits4

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, Header, Position, ncols, nrows, src_pkts, sink_pkts ):
    nterminals = ncols * nrows

    s.src  = [ TestSource( Header, src_pkts[i] ) for i in range( nterminals ) ]
    s.dut  = MeshNetworkMFlitRTL( Header, Position )
    s.sink = [ TestSink( Header, sink_pkts[i] ) for i in range( nterminals ) ]

    for i in range( nterminals ): 
      s.src[i].send //= s.dut.recv[i]
      s.dut.send[i] //= s.sink[i].recv

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
# arrange_src_sink_pkts
#-------------------------------------------------------------------------

def arrange_src_sink_pkts( Header, ncols, nrows, pkt_lst ):
  nterminals = ncols * nrows
  src_pkts  = [ [] for _ in range( nterminals ) ]
  sink_pkts = [ [] for _ in range( nterminals ) ]

  for pkt in pkt_lst:
    header = to_bitstruct( pkt.flits[0], Header )
    src_id = header.src_x.uint() + header.src_y.uint() * ncols
    dst_id = header.dst_x.uint() + header.dst_y.uint() * ncols
    src_pkts [ src_id ].append( pkt )
    sink_pkts[ dst_id ].append( pkt )

  return src_pkts, sink_pkts

#-------------------------------------------------------------------------
# sanity check
#-------------------------------------------------------------------------

def test_sanity_check():
  net = MeshNetworkMFlitRTL( TestHeader, TestPosition, ncols=2, nrows=2 )
  net.elaborate()
  net.apply( SimulationPass() )
  net.sim_reset()
  net.tick()

#-------------------------------------------------------------------------
# test case: basic
#-------------------------------------------------------------------------

def basic_pkts( ncols, nrows ):
  return [
    #       src_x    y        dst_x    y        payload
    mk_pkt(     0,   0,       ncols-1, nrows-1, [ 0x8badf00d             ] ),
    mk_pkt( ncols-1, nrows-1, 0,       0,       [ 0x8badbabe, 0xdeadbeef ] ),
  ]

#-------------------------------------------------------------------------
# test case table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (          'msg_func        ncols  nrows' ),
  [ 'basic',  basic_pkts,     2,     2  ],
])

#-------------------------------------------------------------------------
# test driver
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_mflit_mesh_router( test_params ):
  ncols = test_params.ncols
  nrows = test_params.nrows
  pkts  = test_params.msg_func( ncols, nrows )

  src_pkts, dst_pkts = arrange_src_sink_pkts( TestHeader, ncols, nrows, pkts )

  th = TestHarness( TestHeader, TestPosition, ncols, nrows, 
                    src_pkts, dst_pkts )
  run_sim( th )
