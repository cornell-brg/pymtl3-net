"""
==========================================================================
TorusRouterRTL_test.py
==========================================================================
Tests for TorusRouterRTL.

Author : Yanghui Ou, Cheng Tan
  Date : June 28, 2019
"""
from itertools import product

import pytest

from ocnlib.ifcs.CreditIfc import CreditRecvRTL2SendRTL, RecvRTL2CreditSendRTL
from ocnlib.ifcs.packets import mk_mesh_pkt
from ocnlib.ifcs.positions import mk_mesh_pos
from ocnlib.utils import run_sim
from ocnlib.test.net_sinks import TestNetSinkRTL
from pymtl3 import *
from pymtl3.stdlib.test.test_srcs import TestSrcRTL
from torusnet.TorusRouterFL import TorusRouterFL
from torusnet.TorusRouterRTL import TorusRouterRTL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s,
    PktType   = None,
    src_msgs  = [],
    sink_msgs = [],
    ncols     = 2,
    nrows     = 2 ,
    pos_x     = 0,
    pos_y     = 0,
  ):

    MeshPos = mk_mesh_pos( ncols, nrows )

    match_func = lambda a, b : a.src_x == b.src_x and a.src_y == b.src_y and \
                               a.dst_y == b.dst_y and a.payload == b.payload

    s.srcs  = [ TestSrcRTL( PktType, src_msgs[i] )
                for i in range( 5 ) ]
    s.dut   = TorusRouterRTL( PktType, MeshPos, ncols=ncols, nrows=nrows )
    s.sinks = [ TestNetSinkRTL( PktType, sink_msgs[i], match_func=match_func )
                for i in range( 5 ) ]

    s.src_adapters  = [ RecvRTL2CreditSendRTL( PktType, vc=2 )
                        for _ in range( 5 ) ]
    s.sink_adapters = [ CreditRecvRTL2SendRTL( PktType, vc=2 )
                        for _ in range( 5 ) ]

    # Connections
    for i in range (5):
      s.srcs[i].send          //= s.src_adapters[i].recv
      s.src_adapters[i].send  //= s.dut.recv[i]
      s.dut.send[i]           //= s.sink_adapters[i].recv
      s.sink_adapters[i].send //= s.sinks[i].recv

    s.dut.pos //= MeshPos( pos_x, pos_y )

  def done( s ):
    done = True
    for x in s.srcs:
      done &= x.done()
    for x in s.sinks:
      done &= x.done()
    return done

  def line_trace( s ):
    return f"{s.dut.line_trace()}"

#-------------------------------------------------------------------------
# mk_srcsink_pkts
#-------------------------------------------------------------------------
# A helper function that puts each packet in [lst] into corresponding
# sources and sinks.

def mk_srcsink_pkts( pos_x, pos_y, ncols, nrows, lst ):
  router = TorusRouterFL( pos_x, pos_y, ncols, nrows, dimension='y' )
  src_pkts  = router.arrange_src_pkts( lst )
  sink_pkts = router.route( src_pkts )
  return src_pkts, sink_pkts

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

class TorusRouterRTL_Tests:

  @pytest.mark.parametrize(
    'pos_x, pos_y',
    product( [ 0, 1, 2, 3 ], [ 0, 1, 2, 3 ] )
  )
  def test_simple_4x4( s, pos_x, pos_y, test_verilog ):
    ncols = 4
    nrows = 4

    Pkt = mk_mesh_pkt( ncols, nrows, vc=2 )

    src_pkts, sink_pkts = mk_srcsink_pkts( pos_x, pos_y, ncols, nrows,[
      #   src_x  y  dst_x  y  opq  vc  payload
      Pkt(    0, 0,     1, 1,   0,  0, 0xfaceb00c ),
      Pkt(    0, 0,     0, 0,   0,  0, 0xdeaddead ),
      Pkt(    1, 0,     1, 0,   0,  0, 0xdeadface ),
      Pkt(    0, 2,     3, 3,   0,  0, 0xdeadface ),
    ])

    th = TestHarness( Pkt, src_pkts, sink_pkts )
    th.set_param( "top.construct",
      ncols=ncols, nrows=nrows,
      pos_x=pos_x, pos_y=pos_y,
    )
    run_sim( th, translation="verilog" if test_verilog else '' )

  @pytest.mark.parametrize(
    'pos_x, pos_y',
    product( [ 0, 1, 2, 3, 4, 5 ], [ 0, 1, 2, 3, 4, 5 ] )
  )
  def test_simple_5x5( s, pos_x, pos_y, test_verilog ):
    ncols = 5
    nrows = 5

    Pkt = mk_mesh_pkt( ncols, nrows, vc=2 )

    src_pkts, sink_pkts = mk_srcsink_pkts( pos_x, pos_y, ncols, nrows,[
      #   src_x  y  dst_x  y  opq  vc  payload
      Pkt(    1, 0,     0, 4,   0,  0, 0xfaceb00c ),
    ])

    th = TestHarness( Pkt, src_pkts, sink_pkts )
    th.set_param( "top.construct",
      ncols=ncols, nrows=nrows,
      pos_x=pos_x, pos_y=pos_y,
    )
    run_sim( th, translation="verilog" if test_verilog else '' )
