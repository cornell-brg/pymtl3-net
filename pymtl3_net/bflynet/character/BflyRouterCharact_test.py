#=========================================================================
# BflyRouterCharact_test.py
#=========================================================================
# Used for characterizaing router
#
# Author : Cheng Tan
#   Date : June 16, 2019

import random
import pytest

from pymtl3_net.bflynet.BflyRouterRTL import BflyRouterRTL
from pymtl3_net.bflynet.DTRBflyRouteUnitRTL import DTRBflyRouteUnitRTL
from pymtl3_net.ocnlib.ifcs.packets import mk_bfly_pkt
from pymtl3_net.ocnlib.ifcs.positions import mk_bfly_pos
from pymtl3_net.ocnlib.utils import run_sim
from pymtl3_net.ocnlib.test.stream_sinks import NetSinkRTL as TestNetSinkRTL
from pymtl3 import *
from pymtl3.stdlib.stream.SourceRTL import SourceRTL as TestSrcRTL
from pymtl3_net.router.InputUnitRTL import InputUnitRTL
from pymtl3_net.router.OutputUnitRTL import OutputUnitRTL
from pymtl3_net.router.SwitchUnitRTL import SwitchUnitRTL

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

    print( "=" * 74 )

    num_routers     = n_fly * ( k_ary ** ( n_fly - 1 ) )
    s.num_terminals = k_ary * ( k_ary ** ( n_fly - 1 ) )
    r_rows          = k_ary ** ( n_fly - 1 )
    BflyPos         = mk_bfly_pos( r_rows, n_fly )

    s.dut  = BflyRouterRTL( MsgType, BflyPos, k_ary, n_fly )

    cmp_fn = lambda a,b : a.src == b.src and \
                          a.payload == b.payload and \
                          a.opaque == b.opaque

    s.srcs  = [ TestSrcRTL ( MsgType, src_msgs[i],  src_initial,  src_interval  )
              for i in range ( k_ary ) ]
    s.sinks = [ TestNetSinkRTL ( MsgType, sink_msgs[i], sink_initial,
              sink_interval, cmp_fn = cmp_fn )
              for i in range ( k_ary ) ]

    # Connections

    for i in range ( s.dut.num_outports ):
      s.srcs[i].send //= s.dut.recv[i]
      s.dut.send[i]  //= s.sinks[i].recv

    #TODO: provide pos for router...
    @update
    def up_pos():
      s.dut.pos @= BflyPos( pos_r, pos_f )

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
# Test cases
#-------------------------------------------------------------------------

def set_dst(k_ary, n_fly, vec_dst):

  if k_ary == 1:
    DstType = mk_bits(1)
    return DstType(0)
  DstType = mk_bits( clog2( k_ary ) * n_fly )
  bf_dst = DstType(0)
  tmp = 0
  dst = vec_dst
  for i in range( n_fly ):
    tmp = dst // (k_ary**(n_fly-i-1))
    dst = dst %  (k_ary**(n_fly-i-1))
    bf_dst = DstType(bf_dst | DstType(tmp))
    if i != n_fly - 1:
      if k_ary>2:
        bf_dst = bf_dst * clog2(k_ary)**2
      else:
        bf_dst = bf_dst * 2
  return bf_dst

@pytest.mark.parametrize(
  "src_number",
  # [ 0, 1, 2, 3, 4, 5, 6, 7 ]
  list(range(5))
)
def test_random( src_number ):

  k_ary = 10
  n_fly = 1
  num_terminals = k_ary * ( k_ary ** ( n_fly - 1 ) )
  src_packets   = [ [] for _ in range(k_ary) ]
  sink_packets  = [ [] for _ in range(k_ary) ]
  payload_wid   = 32
  BEGIN = clog2( k_ary ) * n_fly - clog2( k_ary )
  END = clog2( k_ary ) * n_fly
  src = src_number
  pkt_n = 25
  for index in range(pkt_n // k_ary):
    for di in range(k_ary):
      dst = di*(k_ary**(n_fly-1))
#    src = random.randint( 0, k_ary - 1 )
#    dst = random.randint( 0, num_terminals - 1 )

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

  # th.set_param( "top.dut.route_units*.construct", n_fly=n_fly )
  # th.set_param( "top.dut.line_trace",  )

  run_sim( th )

#-------------------------------------------------------------------------
# test_char
#-------------------------------------------------------------------------
# FIXME: (5, 3), (6, 3) doesn't work

@pytest.mark.parametrize(
  'k_ary, n_fly',
  [ (2, 6), (3, 4), (4, 3), (5, 2), (6, 2), (8, 2) ],
)
def test_char( k_ary, n_fly ):

  num_terminals = k_ary * ( k_ary ** ( n_fly - 1 ) )
  src_packets   = [ [] for _ in range(k_ary) ]
  sink_packets  = [ [] for _ in range(k_ary) ]
  payload_wid   = 32

  BEGIN      = clog2( k_ary ) * n_fly - clog2( k_ary )
  END        = clog2( k_ary ) * n_fly
  src        = 0
  PacketType = mk_bfly_pkt( k_ary, n_fly )
  pkt_n      = 25

  for _ in range( pkt_n ):
    for di in range( k_ary ):
      dst     = di*( k_ary**(n_fly-1) )
      bf_dst  = set_dst( k_ary, n_fly, dst )
      payload = random.randint( 0, 2**payload_wid )
      pkt     = PacketType( src, bf_dst, 0, payload)
      src_packets [ src % k_ary ].append( pkt )
      # print( bf_dst, pkt.dst[ BEGIN : END ] )
      sink_packets[ pkt.dst[ BEGIN : END ] ].append( pkt )

  pos_row = 1
  pos_fly = 0

  th = TestHarness( PacketType, k_ary, n_fly, pos_row, pos_fly,
                    src_packets, sink_packets, 0, 0, 0, 0 )

  run_sim( th, cmdline_opts={'dump_vcd':False, 'test_verilog':'zeros', 'dump_vtb':False} )
