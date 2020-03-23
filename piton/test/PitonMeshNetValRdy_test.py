'''
==========================================================================
PitonMeshNetValRdy_test.py
==========================================================================
Test cases for PitonMeshNetValRdy.

Author : Yanghui Ou
  Date : Mar 11, 2020
'''
import pytest
from pymtl3 import *
from pymtl3.stdlib.test import mk_test_case_table
from ocnlib.ifcs.enrdy_adapters import InValRdy2Send, Recv2OutValRdy
from ocnlib.utils import to_bitstruct, run_sim
from ocnlib.packets import MflitPacket as Packet
from ocnlib.test.test_srcs import MflitPacketSourceRTL as TestSource
from ocnlib.test.test_sinks import MflitPacketSinkRTL as TestSink

from ..PitonNoCHeader import PitonNoCHeader
from ..PitonMeshNetValRdy import PitonMeshNetValRdy

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, ncols, nrows, src_pkts, sink_pkts ):
    nterminals = ncols * nrows

    s.src  = [ TestSource( PitonNoCHeader, src_pkts[i] ) for i in range( nterminals+1 ) ]
    s.dut  = PitonMeshNetValRdy( ncols, nrows )
    s.sink = [ TestSink( PitonNoCHeader, sink_pkts[i] ) for i in range( nterminals+1 ) ]

    s.recv2out = [ Recv2OutValRdy( Bits64 ) for _ in range( nterminals+1 ) ]
    s.in2send  = [ InValRdy2Send ( Bits64 ) for _ in range( nterminals+1 ) ]

    for i in  range( nterminals+1 ):
      s.src[i].send     //= s.recv2out[i].recv
      s.in2send[i].send //= s.sink[i].recv

    for i in range( nterminals ):
      s.recv2out[i].out //= s.dut.in_[i]
      s.dut.out[i]      //= s.in2send[i].in_

    s.recv2out[ nterminals ].out //= s.dut.offchip_in
    s.dut.offchip_out            //= s.in2send[ nterminals ].in_

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

n = False
y = True

def mk_pkt( src_offchip, src_x, src_y, dst_offchip, dst_x, dst_y,
            payload=[], fbits=0, mtype=0, mshr=0, opt1=0 ):
  chipid      = b14(1) << 13 if dst_offchip else b14(0)
  plen        = len( payload )
  header      = PitonNoCHeader( chipid, dst_x, dst_y, fbits, plen, mtype, mshr, opt1 )
  header_bits = to_bits( header )
  flits       = [ header_bits ] + payload
  pkt         = Packet( PitonNoCHeader, flits )
  pkt.src_offchip = src_offchip
  pkt.src_x = src_x
  pkt.src_y = src_y
  return pkt

#-------------------------------------------------------------------------
# arrange_src_sink_pkts
#-------------------------------------------------------------------------

def arrange_src_sink_pkts( ncols, nrows, pkt_lst ):
  nterminals = ncols * nrows
  src_pkts  = [ [] for _ in range( nterminals+1 ) ]
  sink_pkts = [ [] for _ in range( nterminals+1 ) ]

  for pkt in pkt_lst:
    header = to_bitstruct( pkt.flits[0], PitonNoCHeader )
    src_id = nterminals if pkt.src_offchip else pkt.src_x + pkt.src_y * ncols
    dst_id = nterminals if header.chipid[13] else header.xpos.uint() + header.ypos.uint() * ncols
    src_pkts [ src_id ].append( pkt )
    sink_pkts[ dst_id ].append( pkt )

  return src_pkts, sink_pkts

#-------------------------------------------------------------------------
# test case: basic
#-------------------------------------------------------------------------

def basic_pkts( ncols, nrows ):
  return [
    #      src                    dst
    #      off       x  y       | off      x  y        payload
    mk_pkt( n,       0, 0,        n, ncols-1, nrows-1, [ 0x8badf00d             ] ),
    mk_pkt( n, ncols-1, nrows-1,  n,       0, 0,       [ 0x8badf00d, 0xdeadbeef ] ),
  ]

#-------------------------------------------------------------------------
# test case: basic offchip
#-------------------------------------------------------------------------

def basic_offchip_pkts( ncols, nrows ):
  return [
    #      src                    dst
    #      off       x  y       | off      x  y        payload
    mk_pkt( y,       0, 0,        n,       0, 0,       [                        ] ),
    mk_pkt( n,       0, 0,        n,       0, 0,       [                        ] ),
  ]

#-------------------------------------------------------------------------
# test case: basic offchip
#-------------------------------------------------------------------------

def offchip_long_pkts( ncols, nrows ):
  return [
    #      src                    dst
    #      off       x  y       | off      x  y        payload
    mk_pkt( y,       0, 0,        n,       0, 0,       [ 0x0100_0000_0100_0000 ] * 8 ),
    mk_pkt( y,       0, 0,        n,       0, 0,       [                       ]     ),
  ]

#-------------------------------------------------------------------------
# test case: basic
#-------------------------------------------------------------------------

def neighbor_pkts( ncols, nrows ):
  pkts = []
  nterminals = ncols * nrows
  for i in range( nterminals ):
    src_x = i %  ncols
    src_y = i // ncols
    dst_x = ( i+1 ) %  ncols
    dst_y = ( ( i+1 ) % nterminals ) // ncols
    payload = [ x for x in range( i % 10 ) ]
    pkts.append( mk_pkt( n, src_x, src_y, n, dst_x, dst_y, payload ) )

  return pkts

#-------------------------------------------------------------------------
# test case table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                'msg_func                ncols  nrows' ),
  [ 'basic',        basic_pkts,             2,     2      ],
  [ 'basic4x4',     basic_pkts,             4,     4      ],
  [ 'basic2x7',     basic_pkts,             2,     7      ],
  [ 'offchip2x7',   basic_offchip_pkts,     2,     7      ],
  [ 'offchip_long', offchip_long_pkts,      2,     7      ],
  [ 'neighbor2x2',  neighbor_pkts,          2,     2      ],
  [ 'neighbor2x3',  neighbor_pkts,          2,     3      ],
  [ 'neighbor3x3',  neighbor_pkts,          3,     3      ],
  [ 'neighbor4x4',  neighbor_pkts,          4,     4      ],
  [ 'neighbor2x7',  neighbor_pkts,          2,     7      ],
])

#-------------------------------------------------------------------------
# test driver
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_piton_mesh( test_params, test_verilog ):
  ncols = test_params.ncols
  nrows = test_params.nrows
  pkts  = test_params.msg_func( ncols, nrows )
  trans_backend = 'verilog' if test_verilog else ''

  src_pkts, dst_pkts = arrange_src_sink_pkts( ncols, nrows, pkts )

  th = TestHarness( ncols, nrows, src_pkts, dst_pkts )
  run_sim( th, translation=trans_backend, xinit=test_verilog )

