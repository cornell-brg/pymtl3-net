#=========================================================================
# BflyFlitNetworkRTL_test.py
#=========================================================================
# Test for BflyFlitNetworkRTL
#
# Author : Cheng Tan, Yanghui Ou
#   Date : April 8, 2019

from pymtl3                        import *
from pymtl3.stdlib.rtl.queues      import NormalQueueRTL
from pymtl3.stdlib.test.test_srcs  import TestSrcRTL
from ocn_pclib.test.net_sinks      import TestNetSinkRTL
from pymtl3.stdlib.test            import TestVectorSimulator
from bflynet.BflyNetworkRTL        import BflyNetworkRTL
from bflynet.BflyFlitNetworkRTL    import BflyFlitNetworkRTL
from ocn_pclib.ifcs.packets        import *
from ocn_pclib.ifcs.flits          import *
from ocn_pclib.ifcs.positions      import *

from pymtl3.passes.sverilog import ImportPass, TranslationPass
from pymtl3.passes import DynamicSim
from bflynet.DTRBflyFlitRouteUnitRTL import DTRBflyFlitRouteUnitRTL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness( Component ):

  def construct( s, MsgType, k_ary, n_fly, src_msgs, sink_msgs,
                 src_initial, src_interval, sink_initial, sink_interval,
                 arrival_time=None ):

    num_routers   = n_fly * ( k_ary ** ( n_fly - 1 ) )
    num_terminals = k_ary * ( k_ary ** ( n_fly - 1 ) )
    r_rows = k_ary ** ( n_fly - 1 )
    BflyPos  = mk_bfly_pos( r_rows, n_fly )
    s.dut  = BflyFlitNetworkRTL( MsgType, BflyPos, k_ary, n_fly, 0)
    
    match_func = lambda a,b : a.payload == b.payload and a.opaque == b.opaque
    s.srcs  = [ TestSrcRTL ( MsgType, src_msgs[i],  src_initial,  src_interval  )
              for i in range ( s.dut.num_terminals ) ]
    s.sinks = [ TestNetSinkRTL ( MsgType, sink_msgs[i], sink_initial,
              sink_interval, match_func=match_func ) 
              for i in range ( s.dut.num_terminals ) ]

    # Connections
    for i in range ( s.dut.num_terminals ):
      s.connect( s.srcs[i].send, s.dut.recv[i]   )
      s.connect( s.dut.send[i],  s.sinks[i].recv )

  def done( s ):
    srcs_done = 1
    sinks_done = 1
    for i in range( s.dut.num_terminals ):
      if s.srcs[i].done() == 0:
        srcs_done = 0
      if s.sinks[i].done() == 0:
        sinks_done = 0
    return srcs_done and sinks_done

  def line_trace( s ):
#    pass
    return s.dut.line_trace()

#-------------------------------------------------------------------------
# run_rtl_sim
#-------------------------------------------------------------------------

def run_sim( test_harness, max_cycles=100 ):

  # Create a simulator

  test_harness.apply( DynamicSim )
  test_harness.sim_reset()

  # Run simulation

  ncycles = 0
  print ""
  print "{}:{}".format( ncycles, test_harness.line_trace() )
  while not test_harness.done() and ncycles < max_cycles:
    test_harness.tick()
    ncycles += 1
    print "{}:{}".format( ncycles, test_harness.line_trace() )

  # Check timeout

  assert ncycles < max_cycles

  test_harness.tick()
  test_harness.tick()
  test_harness.tick()

#-------------------------------------------------------------------------
# Test cases (specific for 4-ary 2-fly butterfly)
#-------------------------------------------------------------------------
#           src, dst, payload
test_msgs = [ (0,15,0xcdab101), (1,14,0xabcd102), (2,13,0xbcda103), (3,12,0xdcba104),
              (4,11,0xcdab105), (5,10,0xabcd106), (6, 9,0xbcda107), (7, 8,0xdcba108),
              (8, 7,0xcdab109), (9, 6,0xabcd110), (10,5,0xbcda111), (11,4,0xdcba112),
              (12,3,0xcdab113), (13,2,0xabcd114), (14,1,0xbcda115), (15,0,0xdcba116) ]

#test_msgs = [ (0,15,0xcdab10115), (1,14,0xabcd10214) ]

def set_dst(k_ary, n_fly, vec_dst):

  DstType = mk_bits( clog2( k_ary ) * n_fly )
  bf_dst = DstType(0)
  tmp = 0
  dst = vec_dst
  for i in range( n_fly ):
    tmp = dst / (k_ary**(n_fly-i-1))
    dst = dst % (k_ary**(n_fly-i-1))
    bf_dst = DstType(bf_dst | DstType(tmp))
    if i != n_fly - 1:
      if k_ary == 1:
        bf_dst = bf_dst * 2
      else:
        bf_dst = bf_dst * k_ary
  return bf_dst

def test_srcsink_2ary_4fly():
  src_flits  =  [ [],[],[],[],
                    [],[],[],[],
                    [],[],[],[],
                    [],[],[],[] ]
  
  sink_flits =  [ [],[],[],[],
                    [],[],[],[],
                    [],[],[],[],
                    [],[],[],[] ]
  k_ary = 2
  n_fly = 4
  opaque_nbits = 1
  nvcs = 1
  payload_nbits = 32
  flit_size = 16
  FlitType = mk_bfly_flit( k_ary, n_fly, 0,
             opaque_nbits, total_flit_nbits=flit_size, nvcs=nvcs )
  for (vec_src, vec_dst, payload) in test_msgs:
    PacketType  = mk_bfly_pkt( k_ary, n_fly, nvcs, opaque_nbits, payload_nbits )
    bf_dst = set_dst( k_ary, n_fly, vec_dst)
    pkt = PacketType( vec_src, bf_dst, 0, payload)
    flits = flitisize_bfly_flit( pkt, k_ary, n_fly,
            opaque_nbits, nvcs, payload_nbits, flit_size )
    src_flits [vec_src] += flits
    sink_flits[vec_dst] += flits 
#    src_packets [vec_src].append( pkt )
#    sink_packets[vec_dst].append( pkt )

  th = TestHarness( FlitType, k_ary, n_fly, src_flits, sink_flits, 
                    0, 0, 0, 0 )

  th.set_param( "top.dut.routers*.route_units*.construct", n_fly=n_fly )
  th.set_param( "top.dut.routers*.construct", k_ary=k_ary )
  th.set_param( "top.dut.routers*.construct", RouteUnitType=DTRBflyFlitRouteUnitRTL )

  run_sim( th )

