'''
==========================================================================
PitonRouter_test.py
==========================================================================
Test cases for Piton mesh router.

NOTE - OpenPiton's coordinate system looks like this:

0 ------------------> x
 | (0, 0)  (1, 0)
 | (0, 1)  (1, 1)
 | ...
 |
 | (0, 6)  (1, 6)
 v
y

Author : Yanghui Ou
  Date : Mar 4, 2020
'''
import pytest
from pymtl3 import *
from pymtl3.stdlib.test_utils import mk_test_case_table
from ocnlib.ifcs.enrdy_adapters import InValRdy2Send, Recv2OutValRdy
from ocnlib.utils import run_sim
from ocnlib.packets import MflitPacket as Packet
from ocnlib.test.test_srcs import MflitPacketSourceRTL as TestSource
from ocnlib.test.test_sinks import MflitPacketSinkRTL as TestSink

from ..PitonNoCHeader import PitonNoCHeader
from ..PitonRouterValRdy import PitonRouterValRdy
from ..PitonRouterFL import PitonRouterFL

#-------------------------------------------------------------------------
# bitstructs for testing
#-------------------------------------------------------------------------

@bitstruct
class PitonPosition:
  pos_x : Bits8
  pos_y : Bits8

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, pos_x, pos_y, src_pkts, sink_pkts ):
    nports = 5

    s.src  = [ TestSource( PitonNoCHeader, src_pkts[i] ) for i in range( nports ) ]
    s.dut  = PitonRouterValRdy( PitonPosition )
    s.sink = [ TestSink( PitonNoCHeader, sink_pkts[i] ) for i in range( nports ) ]

    s.recv2out = [ Recv2OutValRdy( Bits64 ) for _ in range( nports ) ]
    s.in2send  = [ InValRdy2Send ( Bits64 ) for _ in range( nports ) ]

    for i in range( nports ):
      s.src[i].send     //= s.recv2out[i].recv
      s.recv2out[i].out //= s.dut.in_[i]
      s.dut.out[i]      //= s.in2send[i].in_
      s.in2send[i].send //= s.sink[i].recv

    s.dut.pos //= PitonPosition( pos_x, pos_y )

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
# sanity check
#-------------------------------------------------------------------------

def test_sanity_check():
  dut = PitonRouterValRdy( PitonPosition )
  dut.elaborate()
  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()

#-------------------------------------------------------------------------
# constatns
#-------------------------------------------------------------------------

y = True
n = False

#-------------------------------------------------------------------------
# test case: basic
#-------------------------------------------------------------------------

def basic_pkts( pos_x, pos_y ):
  return [
    #      src                dst
    #      off     x  y     | off x     y      payload
    mk_pkt( n,     0, 0,      n, pos_x, pos_y, [ 0x8badf00d             ] ),
    mk_pkt( n, pos_x, pos_y,  n,     0, 0,     [ 0x8badf00d, 0xdeadbeef ] ),
  ]

#-------------------------------------------------------------------------
# test case: hotspot
#-------------------------------------------------------------------------

def hotspot_pkts( pos_x, pos_y ):
  return [
    #      src                dst
    #      off     x  y     | off x     y      payload
    mk_pkt( n,     0, 0,      n, pos_x, pos_y, [ 0x8badf00d                         ] ),
    mk_pkt( n,     0, 1,      n, pos_x, pos_y, [ 0x8badf00d, 0xdeadbeef             ] ),
    mk_pkt( n, pos_x, 0,      n, pos_x, pos_y, [                                    ] ),
    mk_pkt( n,     2, pos_y,  n, pos_x, pos_y, [ 0xdeadbeef, 0xfaceb00c, 0xdeadfa11 ] ),
    mk_pkt( n,     2, pos_y,  n, pos_x, pos_y, [                                    ] ),
    mk_pkt( n,     2, pos_y,  n, pos_x, pos_y, [ 0xdeadc0de ] * 10                   ),
  ]

#-------------------------------------------------------------------------
# test case: long
#-------------------------------------------------------------------------

def long_pkts( pos_x, pos_y ):
  return [
    #      src                dst
    #      off     x  y     | off x     y      payload
    mk_pkt( n,     0, 0,      n, pos_x, pos_y, [ 0x8badf00d                         ] * 13 ),
    mk_pkt( n,     0, 1,      n, pos_x, pos_y, [ 0x8badf00d, 0xdeadbeef             ] * 6  ),
    mk_pkt( n, pos_x, 0,      n, pos_x, pos_y, [                                    ]      ),
    mk_pkt( n,     2, 1,      n, pos_x, pos_y, [ 0xdeadbeef, 0xfaceb00c, 0xdeadfa11 ] * 3  ),
    mk_pkt( n,     7, pos_y,  n, pos_x, pos_y, [                                    ]      ),
    mk_pkt( n,     0, 8,      n, pos_x, pos_y, [ 0xdeadc0de                         ] * 10 ),
  ]

#-------------------------------------------------------------------------
# test case: offchip
#-------------------------------------------------------------------------

def offchip_pkts( pos_x, pos_y ):
  return [
    #      src                dst
    #      off     x  y     | off x     y      payload
    mk_pkt( y,     0, 0,      n, pos_x, pos_y, [ 0x8badcafe                         ] * 13 ),
    mk_pkt( n,     0, 0,      n, pos_x, pos_y, [ 0x8badf00d, 0xdeadbeef             ] * 6  ),
    mk_pkt( n,     1, 1,      y,     0, 0,     [ 0x01badbed,                        ] * 1  ),
    mk_pkt( y,     0, 0,      n,     1, 6,     [                                    ]      ),
    mk_pkt( n, pos_x, pos_y,  y,     0, 0,     [ 0xbad0 + i for i in range(10)      ]      ),
    mk_pkt( n,     0, 6,      y,     0, 0,     [ 0xdeadbeef                         ]      ),
    mk_pkt( y,     0, 0,      n, pos_x, 0,     [                                    ]      ),
  ]# 


#-------------------------------------------------------------------------
# test case table
#-------------------------------------------------------------------------

table = [
  (               'msg_func      pos_x  pos_y' ),
  [ 'basic',       basic_pkts,       1,     1  ],
  [ 'hotspot2_3',  hotspot_pkts,     1,     3  ],
  [ 'hotspot4_4',  hotspot_pkts,     1,     4  ],
  [ 'long_4_4',    long_pkts,        0,     4  ],
]

for x in range(2):
  for y in range(7):
    table.append([ f'hotspot_{x},{y}', hotspot_pkts, x, y ])

for x in range(2):
  for y in range(7):
    table.append([ f'long_{x},{y}', long_pkts, x, y ])

for x in range(2):
  for y in range(7):
    table.append([ f'offchip_{x},{y}', offchip_pkts, x, y ])

test_case_table = mk_test_case_table( table )

#-------------------------------------------------------------------------
# test driver
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_mflit_mesh_router( test_params ):
  ref  = PitonRouterFL( test_params.pos_x, test_params.pos_y )
  pkts = test_params.msg_func( test_params.pos_x, test_params.pos_y )

  src_pkts = ref.arrange_src_pkts( pkts )
  dst_pkts = ref.route( src_pkts )

  th = TestHarness( test_params.pos_x, test_params.pos_y, src_pkts, dst_pkts )
  run_sim( th )
