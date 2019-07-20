#=========================================================================
# RingNetworkRTL_test.py
#=========================================================================
# Test for RingNetworkRTL
#
# Author : Yanghui Ou
#   Date : June 28, 2019

from pymtl3 import *

from pymtl3.stdlib.test.test_srcs import TestSrcRTL
from ocn_pclib.test.net_sinks import TestNetSinkRTL

from ocn_pclib.ifcs.packets import mk_ring_pkt
from ocn_pclib.ifcs.flits   import *
from ocn_pclib.ifcs.positions import mk_ring_pos
from ringnet.RingNetworkRTL import RingNetworkRTL
from ..RingNetworkFL import ringnet_fl

from ringnet.RingFlitRouteUnitRTL import RingFlitRouteUnitRTL

from copy import deepcopy

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
      s.connect( s.srcs[i].send, s.dut.recv[i]   )
      s.connect( s.dut.send[i],  s.sinks[i].recv )

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

class RingNetwork_Tests( object ):

  @classmethod
  def setup_class( cls ):
    cls.DutType = RingNetworkRTL

  def run_sim( s, th, max_cycles=20 ):
    th.elaborate()
    th.apply( SimulationPass )
    th.sim_reset()

    # Run simulation
    ncycles = 0
    print ""
    print "{:3}:{}".format( ncycles, th.line_trace() )
    while not th.done() and ncycles < max_cycles:
      th.tick()
      ncycles += 1
      print "{:3}:{}".format( ncycles, th.line_trace() )

    # Check timeout
    assert ncycles < max_cycles

  def test_simple( s ):
    nterminals = 4
    Pkt = mk_ring_pkt( nterminals )
    src_pkts = mk_src_pkts( nterminals, [
      #    src  dst opq vc payload
      Pkt( 3,   0,  0,  0, 0xfaceb00c ),
    ])
    dst_pkts = ringnet_fl( src_pkts )
    th = TestHarness( Pkt, nterminals, src_pkts, dst_pkts )
    s.run_sim( th )

  def test_cycle( s ):
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
    s.run_sim( th )

  def test_anti_cycle( s ):
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
    s.run_sim( th )

  def test_simple_flit( s ):
    nterminals = 4
    opaque_nbits = 1
    nvcs = 2
    payload_nbits = 32
    flit_size = 16

    PktType = mk_ring_pkt( nterminals, opaque_nbits, nvcs, 
              payload_nbits )
    FlitType = mk_ring_flit( nterminals, 0, opaque_nbits, nvcs, 
               flit_size )
    pkt = PktType( 3,  0,  0,  0, 0xfaceb00c )
    flits    = flitisize_ring_flit( pkt, nterminals, opaque_nbits, nvcs,
               payload_nbits, flit_size )
    src_flits = [ [], [], [], flits ]
    dst_flits = [ flits, [], [], [] ]
    th = TestHarness( FlitType, nterminals, src_flits, dst_flits )
    th.set_param( "top.dut.routers*.construct", 
                  RouteUnitType=RingFlitRouteUnitRTL)
    s.run_sim( th )
