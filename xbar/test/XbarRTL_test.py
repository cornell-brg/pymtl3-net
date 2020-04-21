'''
==========================================================================
XbarRTL_test.py
==========================================================================
Unit tests for XbarRTL.

Author : Yanghui Ou
  Date : Apr 16, 2020
'''
import pytest
from pymtl3 import *
from pymtl3.stdlib.test import mk_test_case_table
from pymtl3.stdlib.test.test_srcs import TestSrcRTL as TestSource
from ocnlib.ifcs.packets import mk_generic_pkt, mk_xbar_pkt
from ocnlib.utils import run_sim
from ocnlib.test.net_sinks import TestNetSinkRTL as TestSink

from ..XbarRTL import XbarRTL

#-------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------

opaque_nbits  = 8
payload_nbits = 32

#-------------------------------------------------------------------------
# test case: sanity check
#-------------------------------------------------------------------------

def test_sanity():
  PktT = mk_generic_pkt( nrouters=4, opaque_nbits=8, vc=0, payload_nbits=32 )
  dut = XbarRTL( PktT, 2, 2 )
  dut.elaborate()
  dut.apply( SimulationPass() )
  dut.sim_reset()
  dut.tick()
  dut.tick()

#-------------------------------------------------------------------------
# arrange_src_sink_pkts
#-------------------------------------------------------------------------

def arrange_src_sink_pkts( num_inports, num_outports, pkt_lst ):
  src_pkts  = [ [] for _ in range( num_inports  ) ]
  sink_pkts = [ [] for _ in range( num_outports ) ]

  for pkt in pkt_lst:
    src = pkt.src.uint()
    dst = pkt.dst.uint()
    src_pkts [ src ].append( pkt )
    sink_pkts[ dst ].append( pkt )

  return src_pkts, sink_pkts

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, num_inports, num_outports, pkts ):
    src_pkts, sink_pkts = \
      arrange_src_sink_pkts( num_inports, num_outports, pkts )

    PktT = mk_xbar_pkt( num_inports, num_outports, opaque_nbits, payload_nbits )
    s.src  = [ TestSource( PktT, src_pkts[i] ) for i in range( num_inports ) ]
    s.dut  = XbarRTL( PktT, num_inports, num_outports )
    s.sink = [ TestSink( PktT, sink_pkts[i] ) for i in range( num_outports ) ]

    for i in range( num_inports ):
      s.src[i].send //= s.dut.recv[i]

    for i in range( num_outports ):
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
# test case: basic
#-------------------------------------------------------------------------

def basic_pkts( n_in, n_out ):
  Pkt = mk_xbar_pkt( n_in, n_out, opaque_nbits, payload_nbits )
  return [
    Pkt( 0, 0, 0x01, 0xfaceb00c ),
  ]

#-------------------------------------------------------------------------
# test case table
#-------------------------------------------------------------------------

test_cases = [
  (                      'msg_func         n_in n_out init intv' ),
  [ 'basic2x2',           basic_pkts,      2,   2,    0,   0     ],
]

test_case_table = mk_test_case_table( test_cases )

#-------------------------------------------------------------------------
# test driver
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_sflit_xbar( test_params, test_verilog ):
  pkts = test_params.msg_func( test_params.n_in, test_params.n_out )
  trans_backend = 'verilog' if test_verilog else ''
  th = TestHarness( test_params.n_in, test_params.n_out, pkts )
  th.set_param( 'top.sink*.construct',
    initial_delay  = test_params.init,
    interval_delay = test_params.intv,
  )
  run_sim( th, translation=trans_backend )
