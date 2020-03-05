'''
==========================================================================
PitonRouteUnit_test.py
==========================================================================
Unit tests for the multi-flit mesh route unit.

Author : Yanghui Ou
  Date : 11 Feb, 2020
'''
import pytest
from pymtl3 import *
from pymtl3.stdlib.test import mk_test_case_table

from pymtl3.stdlib.rtl.queues import BypassQueueRTL
from ocnlib.utils import to_bits, to_bitstruct, run_sim
from ocnlib.test.test_srcs import MflitPacketSourceRTL as TestSource
from ocnlib.test.test_sinks import MflitPacketSinkRTL as TestSink
from ocnlib.packets import MflitPacket as Packet

from ..directions import *
from ..PitonRouteUnit import PitonRouteUnit
from ..PitonNoCHeader import PitonNoCHeader

#-------------------------------------------------------------------------
# Helper stuff
#-------------------------------------------------------------------------

def route_unit_fl( pkt_lst, pos_x, pos_y, ncols, nrows, first_dimension='x' ):
  sink_pkts = [ [] for _ in range(5) ]
  if first_dimension == 'x':
    for pkt in pkt_lst:
      header = to_bitstruct( pkt.flits[0], PitonNoCHeader )
      if header.chipid[13] and pos_x == 0 and pos_y == nrows-1:
        sink_pkts[ WEST ].append( pkt ) # North west port is the offchip port

      elif header.xpos == pos_x and header.ypos == pos_y:
        sink_pkts[ SELF ].append( pkt )
      elif header.xpos < pos_x:
        sink_pkts[ WEST ].append( pkt )
      elif header.xpos > pos_x:
        sink_pkts[ EAST ].append( pkt )
      elif header.ypos < pos_y:
        sink_pkts[ SOUTH ].append( pkt )
      else:
        sink_pkts[ NORTH ].append( pkt )

  elif first_dimension == 'y':
    for pkt in pkt_lst:
      header = to_bitstruct( pkt.flits[0], PitonNoCHeader )
      if header.chipid[13] and pos_x == 0 and pos_y == nrows-1:
        sink_pkts[ WEST ].append( pkt ) # North west port is the offchip port

      elif header.xpos == pos_x and header.ypos == pos_y:
        sink_pkts[ SELF ].append( pkt )
      elif s.header.ypos < pos_y:
        sink_pkts[ NORTH ].append( pkt )
      elif s.header.ypos > pos_y:
        sink_pkts[ SOUTH ].append( pkt )
      elif s.header.xpos < pos_x:
        sink_pkts[ WEST ].append( pkt )
      else:
        sink_pkts[ EAST ].append( pkt )

  else:
    assert False

  return sink_pkts

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):
  def construct( s, PositionType, pkts, x, y, ncols, nrows ):
    PhitType  = Bits64
    sink_pkts = route_unit_fl( pkts, x, y, ncols, nrows )

    s.src   = TestSource( PitonNoCHeader, pkts )
    s.src_q = BypassQueueRTL( PhitType, num_entries=1 )
    s.dut   = PitonRouteUnit( PositionType, ncols, nrows )
    s.sink  = [ TestSink( PitonNoCHeader, sink_pkts[i] ) for i in range(5) ]

    s.src.send  //= s.src_q.enq
    s.src_q.deq //= s.dut.get
    s.dut.pos   //= PositionType( x, y )

    for i in range(5):
      s.sink[i].recv.msg //= s.dut.give[i].ret
      s.sink[i].recv.en  //= lambda: s.dut.give[i].rdy & s.sink[i].recv.rdy
      s.dut.give[i].en   //= lambda: s.dut.give[i].rdy & s.sink[i].recv.rdy

  def done( s ):
    sinks_done = True
    for sink in s.sink:
      sinks_done &= sink.done()
    return s.src.done() and sinks_done

  def line_trace( s ):
    return s.dut.line_trace()

#-------------------------------------------------------------------------
# TestPosition
#-------------------------------------------------------------------------

@bitstruct
class PitonPosition:
  pos_x : Bits8
  pos_y : Bits8

#-------------------------------------------------------------------------
# mk_pkt
#-------------------------------------------------------------------------

def mk_pkt( offchip, dst_x, dst_y, payload=[], fbits=0, mtype=0, mshr=0, opt1=0 ):
  chipid      = b14(1) << 13 if offchip else b14(0)
  plen        = len( payload )
  header      = PitonNoCHeader( chipid, dst_x, dst_y, fbits, plen, mtype, mshr, opt1 )
  header_bits = to_bits( header )
  flits       = [ header_bits ] + payload
  return Packet( PitonNoCHeader, flits )

#-------------------------------------------------------------------------
# test_1pkt
#-------------------------------------------------------------------------

def test_1pkt():
  pkts= [
    mk_pkt( False, 0, 1, [ 0xfaceb00c, 0x8badf00d ] ),
  ]
  th = TestHarness( PitonPosition, pkts, 0, 0, 2, 7 )
  run_sim( th, max_cycles=20 )

#-------------------------------------------------------------------------
# test_4pkt
#-------------------------------------------------------------------------

def test_4pkt():
  pkts= [
    mk_pkt( False, 1, 0, [                                    ] ),
    mk_pkt( False, 1, 2, [ 0xfaceb00c, 0x8badf00d             ] ),
    mk_pkt( False, 0, 1, [ 0xdeadbeef                         ] ),
    mk_pkt( False, 2, 1, [ 0xcafef00d, 0x111edcba, 0xbaaaaaad ] ),
  ]
  th = TestHarness( PitonPosition, pkts, 1, 1, 4, 4 )
  th.set_param( 'top.src.construct', packet_interval_delay = 1 )
  run_sim( th, max_cycles=20 )

#-------------------------------------------------------------------------
# test case: offchip
#-------------------------------------------------------------------------

def offchip_pkts():
  return [
         # offchip   xpos  ypos  payload
   mk_pkt( True,     0,    6,    [ 0x8badf00d_faceb00c                      ] ),
   mk_pkt( True,     0,    6,    [                                          ] ),
   mk_pkt( True,     0,    6,    [ 0x8badf00d_faceb00c, 0xbaaaaaad_f000000d ] ),
  ]

#-------------------------------------------------------------------------
# test case: mix
#-------------------------------------------------------------------------
# Packets goes to the north west (0,6) terminal

def mix_pkts():
  return [
         # offchip xpos  ypos  payload
   mk_pkt( True,   0,    6,    [ 0x8badf00d_faceb00c                      ] ),
   mk_pkt( False,  0,    6,    [                                          ] ),
   mk_pkt( True,   0,    6,    [ 0x8badf00d_faceb00c, 0xbaaaaaad_f000000d ] ),
   mk_pkt( False,  0,    6,    [ 0x11111111_aaaaaaaa, 0x000edcba_badaceee ] ),
  ]


#-------------------------------------------------------------------------
# test case table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                'msg_func      pos_x pos_y' ),
  [ 'offchip_0_6',  offchip_pkts, 0,    6      ],
  [ 'offchip_1_6',  offchip_pkts, 1,    6      ],
  [ 'offchip_0_5',  offchip_pkts, 0,    5      ],
  [ 'mix_0_6',      mix_pkts,     0,    6      ],

])

#-------------------------------------------------------------------------
# test driver
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_piton_router_2x7( test_params ):
  pkts  = test_params.msg_func()
  pos_x = test_params.pos_x
  pos_y = test_params.pos_y
  th = TestHarness( PitonPosition, pkts, pos_x, pos_y, 2, 7 )
  run_sim( th )