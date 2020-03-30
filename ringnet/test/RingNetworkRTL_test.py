"""
=========================================================================
RingNetworkRTL_test.py
=========================================================================
Test for RingNetworkRTL

Author : Yanghui Ou, Cheng Tan
  Date : June 28, 2019
"""
from ocnlib.ifcs.packets import mk_ring_pkt
from ocnlib.ifcs.positions import mk_ring_pos
from ocnlib.utils import run_sim
from ocnlib.test.net_sinks import TestNetSinkRTL
from pymtl3 import *
from pymtl3.stdlib.test.test_srcs import TestSrcRTL
from ringnet.RingNetworkRTL import RingNetworkRTL

from ..RingNetworkFL import ringnet_fl

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, MsgType, num_routers, src_msgs, sink_msgs ):

    s.num_routers = num_routers
    RingPos = mk_ring_pos( num_routers )
    match_func = lambda a, b : a.payload == b.payload

    s.srcs  = [ TestSrcRTL( MsgType, src_msgs[i] )
              for i in range( num_routers ) ]
    s.dut   = RingNetworkRTL( MsgType, RingPos, num_routers, 0)
    s.sinks = [ TestNetSinkRTL( MsgType, sink_msgs[i],
              match_func = match_func )
              for i in range( num_routers ) ]

    # Connections
    for i in range ( s.dut.num_routers ):
      s.srcs[i].send //= s.dut.recv[i]
      s.dut.send[i]  //= s.sinks[i].recv

  def done( s ):
    srcs_done = True
    sinks_done = True
    for i in range( s.num_routers ):
      srcs_done = srcs_done and s.srcs[i].done()
      sinks_done = sinks_done and s.sinks[i].done()
    return srcs_done and sinks_done

  def line_trace( s ):
    return s.dut.line_trace()

#-------------------------------------------------------------------------
# mk_src_pkts
#-------------------------------------------------------------------------

def mk_src_pkts( nterminals, lst ):
  src_pkts = [ [] for _ in range( nterminals ) ]
  src = 0
  for pkt in lst:
    if hasattr(pkt, 'fl_type'):
      if pkt.fl_type == 0:
        src = pkt.src
    else:
      src = pkt.src
    src_pkts[ src ].append( pkt )
  return src_pkts

#=========================================================================
# Test cases
#=========================================================================

class RingNetwork_Tests:

  @classmethod
  def setup_class( cls ):
    cls.DutType = RingNetworkRTL

  # Refactor common test functinos
  def _test_simple( s, translation='' ):
    nterminals = 4
    Pkt = mk_ring_pkt( nterminals )
    src_pkts = mk_src_pkts( nterminals, [
      #    src  dst opq vc payload
      Pkt( 3,   0,  0,  0, 0xfaceb00c ),
    ])
    dst_pkts = ringnet_fl( src_pkts )
    th = TestHarness( Pkt, nterminals, src_pkts, dst_pkts )
    run_sim( th, translation=translation )

  def _test_cycle( s, translation='' ):
    nterminals = 4
    Pkt = mk_ring_pkt( nterminals )
    src_pkts = mk_src_pkts( nterminals, [
      #    src  dst opq vc payload
      Pkt( 0,   1,  0,  0, 0xfaceb00c ),
      Pkt( 1,   2,  1,  0, 0xdeadbeef ),
      Pkt( 2,   3,  2,  0, 0xbaadface ),
      Pkt( 3,   0,  0,  0, 0xfaceb00c ),
    ])
    dst_pkts = ringnet_fl( src_pkts )
    th = TestHarness( Pkt, nterminals, src_pkts, dst_pkts )
    run_sim( th, translation=translation )

  def _test_anti_cycle( s, translation='' ):
    nterminals = 4
    Pkt = mk_ring_pkt( nterminals )
    src_pkts = mk_src_pkts( nterminals, [
      #    src  dst opq vc payload
      Pkt( 0,   3,  0,  0, 0xfaceb00c ),
      Pkt( 1,   0,  1,  0, 0xdeadbeef ),
      Pkt( 2,   1,  2,  0, 0xbaadface ),
      Pkt( 3,   2,  0,  0, 0xfaceb00c ),
    ])
    dst_pkts = ringnet_fl( src_pkts )
    th = TestHarness( Pkt, nterminals, src_pkts, dst_pkts )
    run_sim( th, translation=translation )

  # Run each test with two additional backends
  def test_simple( self ):
    self._test_simple()

  def test_cycle( self ):
    self._test_cycle()

  def test_anti_cycle( self ):
    self._test_anti_cycle()

  def test_simple_verilog( self ):
    self._test_simple('verilog')

  def test_cycle_verilog( self ):
    self._test_cycle('verilog')

  def test_anti_cycle_verilog( self ):
    self._test_anti_cycle('verilog')

  # def test_simple_yosys( self ):
    # self._test_simple('yosys')

  # def test_cycle_yosys( self ):
    # self._test_cycle('yosys')

  # def test_anti_cycle_yosys( self ):
    # self._test_anti_cycle('yosys')
