#=========================================================================
# BflyNetworkRTL_test.py
#=========================================================================
# Test for BflyNetworkRTL
#
# Author : Cheng Tan, Yanghui Ou
#   Date : April 8, 2019

from bflynet.BflyNetworkRTL import BflyNetworkRTL
from ocn_pclib.ifcs.packets import *
from ocn_pclib.ifcs.positions import *
from ocn_pclib.test import run_sim
from ocn_pclib.test.net_sinks import TestNetSinkRTL
from pymtl3 import *
from pymtl3.passes.backends.sverilog import ImportPass, TranslationPass
from pymtl3.stdlib.rtl.queues import NormalQueueRTL
from pymtl3.stdlib.test import TestVectorSimulator
from pymtl3.stdlib.test.test_srcs import TestSrcRTL

#-------------------------------------------------------------------------
# Test Vector
#-------------------------------------------------------------------------

def run_vector_test( model, PacketType, test_vectors, k_ary, n_fly ):

  def tv_in( model, test_vector ):

    num_routers   = n_fly * ( k_ary ** ( n_fly - 1 ) )
    num_terminals = k_ary * ( k_ary ** ( n_fly - 1 ) )
    r_rows        = k_ary ** ( n_fly - 1 )
    BflyPosition  = mk_bfly_pos( k_ary, n_fly )

    if test_vector[0] != 'x':
      terminal_id = test_vector[0]
      if r_rows == 1 or k_ary == 1:
        DstType = mk_bits( n_fly )
      else:
        DstType = mk_bits( clog2( k_ary ) * n_fly )
      dst = test_vector[1][0]
      bf_dst = DstType(0)
      tmp = 0
      for i in range( n_fly ):
        tmp = dst // (k_ary**(n_fly-i-1))
        dst = dst % (k_ary**(n_fly-i-1))
        bf_dst = DstType(bf_dst | DstType(tmp))
        if i != n_fly - 1:
          if k_ary == 1:
            bf_dst = bf_dst * 2
          else:
            bf_dst = bf_dst * k_ary

      pkt = PacketType( terminal_id, bf_dst, 0, test_vector[1][1])

      # Enable the network interface on specific router
      for i in range (num_terminals):
        model.recv[i].en  = 0
      model.recv[terminal_id].msg = pkt
      model.recv[terminal_id].en  = 1

    for i in range (num_terminals):
      model.send[i].rdy = 1

  def tv_out( model, test_vector ):
    if test_vector[2] != 'x':
      assert model.send[test_vector[2]].msg.payload == test_vector[3]

  model.elaborate()
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()
  model.sim_reset()

def test_vector_2ary_1fly( dump_vcd, test_verilog ):

  k_ary = 2
  n_fly = 1
  num_routers = n_fly * ( k_ary ** ( n_fly - 1 ) )
  r_rows      = k_ary ** ( n_fly - 1 )
  BflyPosition = mk_bfly_pos( k_ary, n_fly )
  BflyPacket   = mk_bfly_pkt( k_ary, n_fly )
  model = BflyNetworkRTL( BflyPacket, BflyPosition, k_ary, n_fly, 0 )

  model.set_param( "top.routers*.construct",
                   k_ary=k_ary )
  model.set_param( "top.routers*.route_units*.construct",
                   n_fly=n_fly )
  model.set_param( "top.routers*.input_units*.construct",
                   QueueType=NormalQueueRTL )

  x = 'x'

  # Specific for wire connection (link delay = 0) in 2x2 Torus topology
  simple_2_test = [
  # terminal [packet]   arr_term   msg
  [  0,    [0,1001],     x,       x  ],
  [  0,    [1,1002],     0,     1001 ],
  [  0,    [1,1003],     1,     1002 ],
  [  0,    [1,1004],     1,     1003 ],
  [  0,    [0,1005],     1,     1004 ],
  [  x,    [0,0000],     1,     1005 ],
  [  x,    [0,0000],     x,       x  ],
  [  x,    [0,0000],     x,       x  ],
  [  x,    [0,0000],     x,       x  ],
  [  x,    [0,0000],     x,       x  ],
  [  x,    [0,0000],     x,       x  ],
  [  x,    [0,0000],     x,       x  ],
  ]

  run_vector_test( model, BflyPacket, simple_2_test, k_ary, n_fly)

def test_vector_2ary_2fly( dump_vcd, test_verilog ):

  k_ary = 2
  n_fly = 2
  num_routers  = n_fly * ( k_ary ** ( n_fly - 1 ) )
  r_rows = k_ary ** ( n_fly - 1 )
  BflyPos = mk_bfly_pos( r_rows, n_fly )
  PacketType   = mk_bfly_pkt( k_ary, n_fly )
  model = BflyNetworkRTL( PacketType, BflyPos, k_ary, n_fly, 0 )

  model.set_param( "top.routers*.route_units*.construct", n_fly=n_fly )

  x = 'x'
  # Specific for wire connection (link delay = 0) in 2x2 bfly topology
  simple_4_test = [
  # terminal [packet]   arr_term   msg
  [  0,      [0,1001],     x,       x  ],
  [  0,      [2,1002],     x,       x  ],
  [  0,      [3,1003],     0,     1001 ],
  [  x,      [0,0000],     2,     1002 ],
  [  0,      [1,1004],     3,     1003 ],
  [  0,      [0,1005],     x,       x  ],
  [  x,      [0,0000],     1,     1004 ],
  [  x,      [0,0000],     0,     1005 ],
  ]

  run_vector_test( model, PacketType, simple_4_test, k_ary, n_fly )

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
    s.dut  = BflyNetworkRTL( MsgType, BflyPos, k_ary, n_fly, 0)

    match_func = lambda a,b : a.payload == b.payload and a.opaque == b.opaque
    s.srcs  = [ TestSrcRTL ( MsgType, src_msgs[i],  src_initial,  src_interval  )
              for i in range ( s.dut.num_terminals ) ]
    s.sinks = [ TestNetSinkRTL ( MsgType, sink_msgs[i], sink_initial,
              sink_interval, match_func=match_func )
              for i in range ( s.dut.num_terminals ) ]

    # Connections
    for i in range ( s.dut.num_terminals ):
      s.srcs[i].send //= s.dut.recv[i]
      s.dut.send[i]  //= s.sinks[i].recv

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
    return s.dut.line_trace()

#-------------------------------------------------------------------------
# Test cases (specific for 4-ary 2-fly butterfly)
#-------------------------------------------------------------------------
test_msgs = [
  # src dst payload
  ( 0,  15, 0xcdab101 ),
  ( 1,  14, 0xabcd102 ),
  ( 2,  13, 0xbcda103 ),
  ( 3,  12, 0xdcba104 ),
  ( 4,  11, 0xcdab105 ),
  ( 5,  10, 0xabcd106 ),
  ( 6,  9,  0xbcda107 ),
  ( 7,  8,  0xdcba108 ),
  ( 8,  7,  0xcdab109 ),
  ( 9,  6,  0xabcd110 ),
  ( 10, 5,  0xbcda111 ),
  ( 11, 4,  0xdcba112 ),
  ( 12, 3,  0xcdab113 ),
  ( 13, 2,  0xabcd114 ),
  ( 14, 1,  0xbcda115 ),
  ( 15, 0,  0xdcba116 )
]

def set_dst(k_ary, n_fly, vec_dst):

  DstType = mk_bits( clog2( k_ary ) * n_fly )
  bf_dst = DstType(0)
  tmp = 0
  dst = vec_dst
  for i in range( n_fly ):
    tmp = dst // (k_ary**(n_fly-i-1))
    dst = dst % (k_ary**(n_fly-i-1))
    bf_dst = DstType(bf_dst | DstType(tmp))
    if i != n_fly - 1:
      if k_ary == 1:
        bf_dst = bf_dst * 2
      else:
        bf_dst = bf_dst * k_ary
  return bf_dst

def test_srcsink_4ary_2fly():
  src_packets  =  [ [],[],[],[],
                    [],[],[],[],
                    [],[],[],[],
                    [],[],[],[] ]

  sink_packets =  [ [],[],[],[],
                    [],[],[],[],
                    [],[],[],[],
                    [],[],[],[] ]
  k_ary = 4
  n_fly = 2
  for (vec_src, vec_dst, payload) in test_msgs:
    PacketType  = mk_bfly_pkt( k_ary, n_fly )
    bf_dst = set_dst( k_ary, n_fly, vec_dst)
    pkt = PacketType( vec_src, bf_dst, 0, payload)
    src_packets [vec_src].append( pkt )
    sink_packets[vec_dst].append( pkt )

  th = TestHarness( PacketType, k_ary, n_fly, src_packets, sink_packets,
                    0, 0, 0, 0 )

  th.set_param( "top.dut.routers*.route_units*.construct", n_fly=n_fly )
  th.set_param( "top.dut.routers*.construct", k_ary=k_ary )
  th.set_param( "top.dut.line_trace",  )

  run_sim( th )
  th.dut.elaborate_physical()
