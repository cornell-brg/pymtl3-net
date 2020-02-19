'''
==========================================================================
XbarRouteUnitMFlitRTL_test.py
==========================================================================
Unit tests for the multi-flit xbar route unit.

Author : Yanghui Ou
  Date : Feb 19, 2020
'''
import pytest
from pymtl3 import *
from pymtl3.stdlib.rtl.queues import BypassQueueRTL
from pymtl3.stdlib.test import mk_test_case_table
from ocnlib.utils import to_bits, to_bitstruct, run_sim
from ocnlib.test.test_srcs import MultiFlitPacketSourceRTL as TestSource
from ocnlib.test.test_sinks import MultiFlitPacketSinkRTL as TestSink
from ocnlib.packets import MultiFlitPacket as Packet

from ..XbarRouteUnitMFlitRTL import XbarRouteUnitMFlitRTL

#-------------------------------------------------------------------------
# route_fl
#-------------------------------------------------------------------------

def route_fl( Header, num_outports, pkt_lst ):
  sink_pkts = [ [] for _ in range( num_outports ) ]
  for pkt in pkt_lst:
    header = to_bitstruct( pkt.flits[0], Header )
    dst    = header.dst.uint()
    sink_pkts[ dst ].append( pkt )
  return sink_pkts

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, Header, num_outports, pkts ):
    PhitType  = mk_bits( get_nbits( Header ) )
    sink_pkts = route_fl( Header, num_outports, pkts )

    s.src   = TestSource( Header, pkts )
    s.src_q = BypassQueueRTL( PhitType, num_entries=1 ) 
    s.dut   = XbarRouteUnitMFlitRTL( Header, num_outports )
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
  flits  = [ to_bits( header) ] + payload
  return Packet( TestHeader, flits )

#--------------------------------------------------------------------------
# test case: 1 pkt
#--------------------------------------------------------------------------

def one_pkt( num_outports ):
  return [ mk_pkt( 0, num_outports-1, [ 0x8badf00d, 0xfaceb00c ] ) ]

#--------------------------------------------------------------------------
# test case table
#--------------------------------------------------------------------------

test_cases = [
  (               'msg_func n_outs init flit_intv pkt_intv' ),
  [ '1pkt',        one_pkt, 4,     0,   0,        0         ],
  [ '1pkt_delay',  one_pkt, 4,     9,   3,        0         ],
]

test_case_table = mk_test_case_table( test_cases )

#--------------------------------------------------------------------------
# test driver
#--------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_xbar_route( test_params, test_verilog ):
  pkts = test_params.msg_func( test_params.n_outs )
  th   = TestHarness( TestHeader, test_params.n_outs, pkts )

  trans_backend = 'yosys' if test_verilog else ''
  run_sim( th, translation=trans_backend )
