'''
==========================================================================
XbarRouteUnitMflitRTL_test.py
==========================================================================
Unit tests for the multi-flit xbar route unit.

Author : Yanghui Ou
  Date : Feb 19, 2020
'''
import pytest
from pymtl3 import *
from pymtl3.stdlib.queues import BypassQueueRTL
from pymtl3.stdlib.test_utils import mk_test_case_table
from ocnlib.utils import run_sim
from ocnlib.test.test_srcs import MflitPacketSourceRTL as TestSource
from ocnlib.test.test_sinks import MflitPacketSinkRTL as TestSink
from ocnlib.packets import MflitPacket as Packet

from ..XbarRouteUnitMflitRTL import XbarRouteUnitMflitRTL

#-------------------------------------------------------------------------
# route_fl
#-------------------------------------------------------------------------

def route_fl( Header, num_outports, pkt_lst ):
  sink_pkts = [ [] for _ in range( num_outports ) ]
  for pkt in pkt_lst:
    header = Header.from_bits( pkt.flits[0] )
    dst    = header.dst.uint()
    sink_pkts[ dst ].append( pkt )
  return sink_pkts

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, Header, num_outports, pkts ):
    PhitType  = mk_bits( Header.nbits )
    sink_pkts = route_fl( Header, num_outports, pkts )

    s.src   = TestSource( Header, pkts )
    s.src_q = BypassQueueRTL( PhitType, num_entries=1 )
    s.dut   = XbarRouteUnitMflitRTL( Header, num_outports )
    s.sink  = [ TestSink( Header, sink_pkts[i] ) for i in range( num_outports ) ]

    s.src.send  //= s.src_q.enq
    s.src_q.deq //= s.dut.get

    for i in range( num_outports ):
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
# TestHeader
#-------------------------------------------------------------------------

@bitstruct
class TestHeader:
  src    : Bits8
  dst    : Bits8
  opaque : Bits8
  plen   : Bits8

#-------------------------------------------------------------------------
# mk_pkt
#-------------------------------------------------------------------------

def mk_pkt( src, dst, payload=[], opaque=0 ):
  plen   = len( payload )
  header = TestHeader( src, dst, opaque, plen )
  flits  = [ header.to_bits() ] + payload
  return Packet( TestHeader, flits )

#--------------------------------------------------------------------------
# test case: 1 pkt
#--------------------------------------------------------------------------

def one_pkt( num_outports ):
  return [ mk_pkt( 0, num_outports-1, [ 0x8badf00d, 0xfaceb00c ] ) ]

#--------------------------------------------------------------------------
# test case: 1 pkt to each
#--------------------------------------------------------------------------

def two_pkt_each( num_outports ):
  pkts = []

  for i in range( num_outports ):
    pkts.append( mk_pkt( 0, i, [ x for x in range( i ) ] ) )

  for i in range( num_outports ):
    pkts.append( mk_pkt( 0, i, [ x for x in range( (i+1) % 5 ) ] ) )

  return pkts

#--------------------------------------------------------------------------
# test case table
#--------------------------------------------------------------------------

test_cases = [
  (                      'msg_func      n_outs init flit_intv pkt_intv' ),
  [ '1pkt',               one_pkt,      4,     0,   0,        0         ],
  [ '1pkt_delay',         one_pkt,      4,     9,   3,        0         ],
  [ '2pkt_each_4',        two_pkt_each, 4,     0,   0,        9         ],
  [ '2pkt_each_4_delay',  two_pkt_each, 4,     4,   4,        0         ],
  [ '2pkt_each_6',        two_pkt_each, 6,     0,   0,        0         ],
  [ '2pkt_each_6_delay',  two_pkt_each, 6,     3,   6,        9         ],
  [ '2pkt_each_8',        two_pkt_each, 4,     0,   0,        0         ],
  [ '2pkt_each_8_delay',  two_pkt_each, 4,     8,   4,        9         ],
]

test_case_table = mk_test_case_table( test_cases )

#--------------------------------------------------------------------------
# test driver
#--------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_xbar_route( test_params, cmdline_opts ):
  pkts = test_params.msg_func( test_params.n_outs )
  th   = TestHarness( TestHeader, test_params.n_outs, pkts )
  th.set_param( 'top.sink*.construct',
    initial_delay         = test_params.init,
    flit_interval_delay   = test_params.flit_intv,
    packet_interval_delay = test_params.pkt_intv,
  )

  run_sim( th, cmdline_opts )
