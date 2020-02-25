#=========================================================================
# MeshRouterRTL_test.py
#=========================================================================
# Test for RouterRTL
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 10, 2019

import hypothesis
from hypothesis import strategies as st

from meshnet.DORXMeshRouteUnitRTL import DORXMeshRouteUnitRTL
from meshnet.DORYMeshRouteUnitRTL import DORYMeshRouteUnitRTL
from meshnet.MeshRouterRTL import MeshRouterRTL
from ocnlib.ifcs.packets import mk_mesh_pkt
from ocnlib.ifcs.positions import mk_mesh_pos
from ocnlib.test import run_sim
from ocnlib.test.net_sinks import TestNetSinkRTL
from pymtl3 import *
from pymtl3.passes.backends.sverilog import ImportPass, TranslationPass
from pymtl3.stdlib.test.test_srcs import TestSrcRTL
from router.InputUnitRTL import InputUnitRTL
from router.OutputUnitRTL import OutputUnitRTL
from router.SwitchUnitRTL import SwitchUnitRTL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s,
                 MsgType       = None,
                 ncols      = 2,
                 nrows       = 2 ,
                 pos_x         = 0,
                 pos_y         = 0,
                 src_msgs      = [],
                 sink_msgs     = [],
                 src_initial   = 0,
                 src_interval  = 0,
                 sink_initial  = 0,
                 sink_interval = 0,
                 arrival_time  =[None, None, None, None, None]
               ):

    MeshPos = mk_mesh_pos( ncols, nrows )
    s.dut = MeshRouterRTL( MsgType, MeshPos, InputUnitType = InputUnitRTL,
        RouteUnitType = DORYMeshRouteUnitRTL )
    match_func = lambda a, b : a.payload == b.payload

    s.srcs  = [ TestSrcRTL    ( MsgType, src_msgs[i],  src_initial,  src_interval  )
                for i in range  ( s.dut.num_inports ) ]
    s.sinks = [ TestNetSinkRTL( MsgType, sink_msgs[i], sink_initial,
                match_func=match_func ) for i in range ( s.dut.num_outports ) ]

    # Connections

    for i in range ( s.dut.num_outports ):
      s.srcs[i].send //= s.dut.recv[i]
      s.dut.send[i]  //= s.sinks[i].recv

    @s.update
    def up_pos():
      s.dut.pos = MeshPos( pos_x, pos_y )

  def done( s ):
    srcs_done = 1
    sinks_done = 1

    for x in s.srcs:
      if x.done() == 0:
        srcs_done = 0

    for x in s.sinks:
      if x.done() == 0:
        sinks_done = 0
    return srcs_done and sinks_done

  def line_trace( s ):
    return "{}".format( s.dut.line_trace() )

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

#              x,y,pl,dir
test_msgs = [[(0,0,11,1),(0,0,12,1),(0,1,13,2),(2,1,14,3),(0,0,15,1)],
             [(0,0,21,1),(0,2,22,0),(0,1,23,2),(2,1,24,3),(2,1,25,3)],
             [(0,2,31,0),(0,0,32,1),(0,1,33,2),(1,1,34,4),(1,1,35,4)]
            ]
result_msgs = [[],[],[],[],[]]

def test_normal_simple():
  src_packets = [[],[],[],[],[]]
  for item in test_msgs:
    for i in range( len( item ) ):
      (dst_x,dst_y,payload,dir_out) = item[i]
      PacketType = mk_mesh_pkt (4, 4)
      pkt = PacketType (0, 0, dst_x, dst_y, 1, payload)
      src_packets[i].append( pkt )
      result_msgs[dir_out].append( pkt )

  th = TestHarness( PacketType, 4, 4, 1, 1, src_packets, result_msgs, 0, 0, 0, 0 )
  run_sim( th )

def test_self_simple():
  PacketType = mk_mesh_pkt(4, 4)
  pkt = PacketType( 0, 0, 0, 0, 0, 0xdead )
  src_pkts  = [ [], [], [], [], [pkt] ]
  sink_pkts = [ [], [], [], [], [pkt] ]
  th = TestHarness( PacketType, 4, 4, 0, 0, src_pkts, sink_pkts )
  run_sim( th )

def test_h1():
  pos_x, pos_y, ncols, nrows = 0, 0, 2, 2
  PacketType = mk_mesh_pkt( ncols, nrows )
  pkt0 = PacketType( 0, 0, 0, 1, 0, 0xdead )
  src_pkts  = [ [],     [], [], [], [pkt0] ]
  sink_pkts = [ [pkt0], [], [], [], []     ]
  th = TestHarness(
    PacketType, ncols, nrows, pos_x, pos_y,
    src_pkts, sink_pkts
  )
  th.set_param(
    "top.dut.construct",
    RouteUnitType = DORYMeshRouteUnitRTL
  )
  run_sim( th )

def test_h2():
  pos_x, pos_y, ncols, nrows = 0, 0, 2, 2
  PacketType = mk_mesh_pkt( ncols, nrows )
  pkt0 = PacketType( 0, 0, 1, 0, 0, 0xdead )
  pkt1 = PacketType( 0, 1, 1, 0, 1, 0xbeef )
  pkt2 = PacketType( 0, 1, 1, 0, 2, 0xcafe )
              # N             S   W   E                   self
  src_pkts  = [ [pkt1, pkt2], [], [], [],                 [pkt0] ]
  sink_pkts = [ [],           [], [], [pkt1, pkt0, pkt2], []     ]
  th = TestHarness(
    PacketType, ncols, nrows, pos_x, pos_y,
    src_pkts, sink_pkts
  )
  th.set_param(
    "top.dut.construct",
    RouteUnitType = DORYMeshRouteUnitRTL
  )
  run_sim( th, 10 )

def test_h3():
  pos_x, pos_y, ncols, nrows = 0, 1, 2, 2
  PacketType = mk_mesh_pkt( ncols, nrows )
  pkt0 = PacketType( 0, 1, 0, 0, 0, 0xdead )
              # N   S   W   E   self
  src_pkts  = [ [], [], [], [], [pkt0] ]
  sink_pkts = [ [], [pkt0], [], [], [] ]
  th = TestHarness(
    PacketType, ncols, nrows, pos_x, pos_y,
    src_pkts, sink_pkts
  )
  th.set_param(
    "top.dut.construct",
    RouteUnitType = DORYMeshRouteUnitRTL
  )
  run_sim( th, 10 )
