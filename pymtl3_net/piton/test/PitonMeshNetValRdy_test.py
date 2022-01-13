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
from pymtl3.stdlib.test_utils import mk_test_case_table
from pymtl3_net.ocnlib.ifcs.enrdy_adapters import InValRdy2Send, Recv2OutValRdy
from pymtl3_net.ocnlib.utils import run_sim
from pymtl3_net.ocnlib.packets import MflitPacket as Packet
from pymtl3_net.ocnlib.test.test_srcs import MflitPacketSourceRTL as TestSource
from pymtl3_net.ocnlib.test.test_sinks import MflitPacketSinkRTL as TestSink

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
  header_bits = header.to_bits()
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
    header = PitonNoCHeader.from_bits( pkt.flits[0] )
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
    # mk_pkt( n,       0, 0,        n, ncols-1, nrows-1, [ 0x8badf00d             ] ),
    mk_pkt( n, ncols-1, nrows-1,  n,       1, 0,       [ 0x8badf00d, 0xdeadbeef ] ),
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
# test case: hotspot
#-------------------------------------------------------------------------

def mk_hotspot_func( dst_x, dst_y, dst_offchip=False ):

  def hotspot_pkts( ncols, nrows ):
    if dst_offchip: assert dst_x == dst_y == 0
    pkts = []
    nterminals = ncols * nrows
    pkts.append( mk_pkt( y, 0, 0, dst_offchip, dst_x, dst_y ) )
    for i in range( nterminals ):
      src_x = i %  ncols
      src_y = i // ncols
      payload = [ x for x in range( i % 10 ) ]
      pkts.append( mk_pkt( n, src_x, src_y, dst_offchip, dst_x, dst_y, payload ) )
    return pkts

  return hotspot_pkts

#-------------------------------------------------------------------------
# test case table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                  'msg_func                ncols  nrows src_init src_pintv  src_fintv sink_init sink_pintv sink_fintv' ),
  [ 'basic',          basic_pkts,             2,     2,    0,       0,         0,       0,        0,          0,          ],
  [ 'basic4x4',       basic_pkts,             4,     4,    0,       0,         0,       0,        0,          0,          ],
  [ 'basic2x7',       basic_pkts,             2,     7,    0,       0,         0,       0,        0,          0,          ],
  [ 'basic2x7_delay', basic_pkts,             2,     7,    0,       0,         0,       20,       0,          0,          ],
  [ 'offchip2x7',     basic_offchip_pkts,     2,     7,    0,       0,         0,       0,        0,          0,          ],
  [ 'long2x7',        offchip_long_pkts,      2,     7,    0,       0,         0,       0,        0,          0,          ],
  [ 'neighbor2x2',    neighbor_pkts,          2,     2,    0,       0,         0,       0,        0,          0,          ],
  [ 'neighbor2x3',    neighbor_pkts,          2,     3,    0,       0,         0,       0,        0,          0,          ],
  [ 'neighbor3x3',    neighbor_pkts,          3,     3,    0,       0,         0,       0,        0,          0,          ],
  [ 'neighbor4x4',    neighbor_pkts,          4,     4,    0,       0,         0,       0,        0,          0,          ],
  [ 'neighbor2x7',    neighbor_pkts,          2,     7,    0,       0,         0,       0,        0,          0,          ],
])

#-------------------------------------------------------------------------
# test case table - specific for 2x7
#-------------------------------------------------------------------------

test_case_table2x7 = mk_test_case_table([
  (                       'msg_func                   src_init src_pintv  src_fintv sink_init sink_pintv sink_fintv' ),
  [ 'basic',               basic_pkts,                0,       0,         0,        0,        0,          0,         ],
  [ 'basic_bp',            basic_pkts,                0,       0,         0,        20,       0,          0,         ],
  [ 'offchip',             basic_offchip_pkts,        0,       0,         0,        0,        0,          0,         ],
  [ 'offchip_bp',          basic_offchip_pkts,        0,       0,         0,        20,       10,         3,         ],
  [ 'long',                offchip_long_pkts,         0,       0,         0,        0,        0,          0,         ],
  [ 'long_bp',             offchip_long_pkts,         0,       0,         0,        10,       15,         5,         ],
  [ 'neighbor',            neighbor_pkts,             0,       0,         0,        0,        0,          0,         ],
  [ 'neighbor_src',        neighbor_pkts,             0,       0,         0,        0,        0,          0,         ],
  [ 'neighbor_bp',         neighbor_pkts,             0,       0,         0,        10,       10,         5,         ],
  [ 'hotspot_offchip',     mk_hotspot_func(0,0,True), 0,       0,         0,        0,        0,          0,         ],
  [ 'hotspot0_0',          mk_hotspot_func(0,0),      0,       0,         0,        0,        0,          0,         ],
  [ 'hotspot0_1',          mk_hotspot_func(0,1),      0,       0,         0,        0,        0,          0,         ],
  [ 'hotspot0_2',          mk_hotspot_func(0,2),      0,       0,         0,        0,        0,          0,         ],
  [ 'hotspot0_3',          mk_hotspot_func(0,3),      0,       0,         0,        0,        0,          0,         ],
  [ 'hotspot0_4',          mk_hotspot_func(0,4),      0,       0,         0,        0,        0,          0,         ],
  [ 'hotspot0_5',          mk_hotspot_func(0,5),      0,       0,         0,        0,        0,          0,         ],
  [ 'hotspot0_6',          mk_hotspot_func(0,6),      0,       0,         0,        0,        0,          0,         ],
  [ 'hotspot1_0',          mk_hotspot_func(1,0),      0,       0,         0,        0,        0,          0,         ],
  [ 'hotspot1_1',          mk_hotspot_func(1,1),      0,       0,         0,        0,        0,          0,         ],
  [ 'hotspot1_2',          mk_hotspot_func(1,2),      0,       0,         0,        0,        0,          0,         ],
  [ 'hotspot1_3',          mk_hotspot_func(1,3),      0,       0,         0,        0,        0,          0,         ],
  [ 'hotspot1_4',          mk_hotspot_func(1,4),      0,       0,         0,        0,        0,          0,         ],
  [ 'hotspot1_5',          mk_hotspot_func(1,5),      0,       0,         0,        0,        0,          0,         ],
  [ 'hotspot1_6',          mk_hotspot_func(1,6),      0,       0,         0,        0,        0,          0,         ],
  [ 'hotspot_offchip_src', mk_hotspot_func(0,0,True), 0,       1,         0,        0,        0,          0,         ],
  [ 'hotspot0_0_src',      mk_hotspot_func(0,0),      0,       2,         1,        0,        0,          0,         ],
  [ 'hotspot0_1_src',      mk_hotspot_func(0,1),      0,       3,         0,        0,        0,          0,         ],
  [ 'hotspot0_2_src',      mk_hotspot_func(0,2),      0,       4,         2,        0,        0,          0,         ],
  [ 'hotspot0_3_src',      mk_hotspot_func(0,3),      0,       5,         0,        0,        0,          0,         ],
  [ 'hotspot0_4_src',      mk_hotspot_func(0,4),      0,       6,         3,        0,        0,          0,         ],
  [ 'hotspot0_5_src',      mk_hotspot_func(0,5),      0,       7,         0,        0,        0,          0,         ],
  [ 'hotspot0_6_src',      mk_hotspot_func(0,6),      0,       8,         4,        0,        0,          0,         ],
  [ 'hotspot1_0_src',      mk_hotspot_func(1,0),      0,       9,         0,        0,        0,          0,         ],
  [ 'hotspot1_1_src',      mk_hotspot_func(1,1),      0,       10,        5,        0,        0,          0,         ],
  [ 'hotspot1_2_src',      mk_hotspot_func(1,2),      0,       11,        0,        0,        0,          0,         ],
  [ 'hotspot1_3_src',      mk_hotspot_func(1,3),      0,       12,        6,        0,        0,          0,         ],
  [ 'hotspot1_4_src',      mk_hotspot_func(1,4),      0,       13,        0,        0,        0,          0,         ],
  [ 'hotspot1_5_src',      mk_hotspot_func(1,5),      0,       14,        7,        0,        0,          0,         ],
  [ 'hotspot1_6_src',      mk_hotspot_func(1,6),      0,       15,        0,        0,        0,          0,         ],
  [ 'hotspot_offchip_bp',  mk_hotspot_func(0,0,True), 0,       0,         0,        10,       0,          0,         ],
  [ 'hotspot0_0_bp',       mk_hotspot_func(0,0),      0,       0,         0,        12,       1,          1,         ],
  [ 'hotspot0_1_bp',       mk_hotspot_func(0,1),      0,       0,         0,        14,       2,          0,         ],
  [ 'hotspot0_2_bp',       mk_hotspot_func(0,2),      0,       0,         0,        16,       3,          2,         ],
  [ 'hotspot0_3_bp',       mk_hotspot_func(0,3),      0,       0,         0,        18,       4,          0,         ],
  [ 'hotspot0_4_bp',       mk_hotspot_func(0,4),      0,       0,         0,        20,       5,          3,         ],
  [ 'hotspot0_5_bp',       mk_hotspot_func(0,5),      0,       0,         0,        22,       6,          0,         ],
  [ 'hotspot0_6_bp',       mk_hotspot_func(0,6),      0,       0,         0,        24,       7,          4,         ],
  [ 'hotspot1_0_bp',       mk_hotspot_func(1,0),      0,       0,         0,        26,       8,          0,         ],
  [ 'hotspot1_1_bp',       mk_hotspot_func(1,1),      0,       0,         0,        28,       9,          5,         ],
  [ 'hotspot1_2_bp',       mk_hotspot_func(1,2),      0,       0,         0,        30,       10,         0,         ],
  [ 'hotspot1_3_bp',       mk_hotspot_func(1,3),      0,       0,         0,        32,       11,         6,         ],
  [ 'hotspot1_4_bp',       mk_hotspot_func(1,4),      0,       0,         0,        34,       12,         0,         ],
  [ 'hotspot1_5_bp',       mk_hotspot_func(1,5),      0,       0,         0,        36,       13,         7,         ],
  [ 'hotspot1_6_bp',       mk_hotspot_func(1,6),      0,       0,         0,        38,       14,         0,         ],
])

#-------------------------------------------------------------------------
# test driver
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_piton_mesh( test_params, cmdline_opts ):
  ncols = test_params.ncols
  nrows = test_params.nrows
  pkts  = test_params.msg_func( ncols, nrows )

  src_pkts, dst_pkts = arrange_src_sink_pkts( ncols, nrows, pkts )

  th = TestHarness( ncols, nrows, src_pkts, dst_pkts )
  th.set_param( 'top.src*.construct', 
    initial_delay         = test_params.src_init,
    packet_interval_delay = test_params.src_pintv,
    flit_interval_delay   = test_params.src_fintv,
  )
  th.set_param( 'top.sink*.construct', 
    initial_delay         = test_params.sink_init,
    packet_interval_delay = test_params.sink_pintv,
    flit_interval_delay   = test_params.sink_fintv,
  )
  run_sim( th, cmdline_opts )

@pytest.mark.parametrize( **test_case_table2x7 )
def test_piton_mesh2x7( test_params, cmdline_opts ):
  ncols = 2
  nrows = 7
  pkts  = test_params.msg_func( ncols, nrows )

  src_pkts, dst_pkts = arrange_src_sink_pkts( ncols, nrows, pkts )

  th = TestHarness( ncols, nrows, src_pkts, dst_pkts )
  th.set_param( 'top.src*.construct',
    initial_delay         = test_params.src_init,
    packet_interval_delay = test_params.src_pintv,
    flit_interval_delay   = test_params.src_fintv,
  )
  th.set_param( 'top.sink*.construct',
    initial_delay         = test_params.sink_init,
    packet_interval_delay = test_params.sink_pintv,
    flit_interval_delay   = test_params.sink_fintv,
  )
  run_sim( th, cmdline_opts )

