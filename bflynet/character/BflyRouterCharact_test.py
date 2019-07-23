#=========================================================================
# BflyRouterCharact_test.py
#=========================================================================
# Used for characterizaing router
#
# Author : Cheng Tan
#   Date : June 16, 2019

from pymtl3                         import *
from pymtl3.stdlib.test.test_srcs   import TestSrcRTL
from ocn_pclib.test.net_sinks       import TestNetSinkRTL
from ocn_pclib.ifcs.positions       import mk_bfly_pos
from ocn_pclib.ifcs.packets         import mk_bfly_pkt
from pymtl3.stdlib.test             import TestVectorSimulator
from bflynet.BflyRouterRTL          import BflyRouterRTL
from bflynet.DTRBflyRouteUnitRTL    import DTRBflyRouteUnitRTL
from router.InputUnitRTL            import InputUnitRTL
from router.OutputUnitRTL           import OutputUnitRTL
from router.SwitchUnitRTL           import SwitchUnitRTL
from pymtl3.passes                  import DynamicSim
from pymtl3.passes.yosys            import ImportPass, TranslationPass

import random

random.seed( 'deadbeef' )

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s,
                 MsgType       = None,
                 k_ary         = 2,
                 n_fly         = 2,
                 pos_r         = 0,
                 pos_f         = 0,
                 src_msgs      = [],
                 sink_msgs     = [],
                 src_initial   = 0,
                 src_interval  = 0,
                 sink_initial  = 0,
                 sink_interval = 0,
                 arrival_time  =[None, None, None, None, None]
               ):

    print "=" * 74

    num_routers   = n_fly * ( k_ary ** ( n_fly - 1 ) )
    s.num_terminals = k_ary * ( k_ary ** ( n_fly - 1 ) )
    r_rows = k_ary ** ( n_fly - 1 )
    BflyPos  = mk_bfly_pos( r_rows, n_fly )

    s.dut  = BflyRouterRTL( MsgType, BflyPos, k_ary )

    match_func = lambda a,b : a.src==b.src and a.payload == b.payload\
        and a.opaque == b.opaque

    s.srcs  = [ TestSrcRTL ( MsgType, src_msgs[i],  src_initial,  src_interval  )
              for i in range ( k_ary ) ]
    s.sinks = [ TestNetSinkRTL ( MsgType, sink_msgs[i], sink_initial,
              sink_interval, match_func = match_func)
              for i in range ( k_ary ) ]

    # Connections

    for i in range ( s.dut.num_outports ):
      s.connect( s.srcs[i].send, s.dut.recv[i]   )
      s.connect( s.dut.send[i],  s.sinks[i].recv )

    #TODO: provide pos for router...
    @s.update
    def up_pos():
      s.dut.pos = BflyPos( pos_r, pos_f )

  def done( s ):
    srcs_done = 1
    sinks_done = 1
#    for i in range( s.dut.num_inports ):
#      if s.srcs[i].done() == 0:
    for x in s.srcs:
      if x.done() == 0:
        srcs_done = 0
#    for i in range( s.dut.num_outports ):
#      if s.sinks[i].done() == 0:
    for x in s.sinks:
      if x.done() == 0:
        sinks_done = 0
    return srcs_done and sinks_done

  def line_trace( s ):
    return "{}".format(
      s.dut.line_trace(),
      #'|'.join( [ s.sinks[i].line_trace() for i in range(5) ] ),
    )

#-------------------------------------------------------------------------
# run_rtl_sim
#-------------------------------------------------------------------------

def run_sim( test_harness, max_cycles=1000 ):

  # Create a simulator
  test_harness.elaborate()
  test_harness.dut.yosys_translate = True
  test_harness.dut.yosys_import = True
  test_harness.dut.dump_vcd = True
  test_harness.apply( TranslationPass() )
  test_harness = ImportPass()( test_harness )
#  test_harness.apply( SimpleSim )
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
# Test cases
#-------------------------------------------------------------------------

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

def test_random():

  k_ary = 10
  n_fly = 3
  num_terminals = k_ary * ( k_ary ** ( n_fly - 1 ) )
  src_packets   = [ [] for _ in range(k_ary) ]
  sink_packets  = [ [] for _ in range(k_ary) ]
  payload_wid   = 8
  BEGIN = clog2( k_ary ) * n_fly - clog2( k_ary )
  END = clog2( k_ary ) * n_fly
  for _ in range(500):
    src = random.randint( 0, k_ary - 1 )
    dst = random.randint( 0, num_terminals - 1 )

    PacketType  = mk_bfly_pkt( k_ary, n_fly )
    bf_dst = set_dst( k_ary, n_fly, dst)
    payload = random.randint( 0, 2**payload_wid )
    pkt = PacketType( src, bf_dst, 0, payload)
    src_packets [ src%k_ary ].append( pkt )
    sink_packets[ pkt.dst[ BEGIN : END ] ].append( pkt )

  pos_row = 1
  pos_fly = 0

  th = TestHarness( PacketType, k_ary, n_fly, pos_row, pos_fly,
                    src_packets, sink_packets, 0, 0, 0, 0 )

  th.set_param( "top.dut.route_units*.construct", n_fly=n_fly )
  th.set_param( "top.dut.line_trace",  )

  run_sim( th )
