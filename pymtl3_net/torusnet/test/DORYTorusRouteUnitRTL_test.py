"""
==========================================================================
DORYTorusRouteUnitRTL_test.py
==========================================================================
Test for DORYTorusRouteUnitRTL

Author : Yanghui Ou
  Date : June 28, 2019
"""
from itertools import product
import pytest

from pymtl3 import *
from pymtl3.stdlib.stream.queues import BypassQueueRTL
from pymtl3.stdlib.stream.SourceRTL import SourceRTL as TestSrcRTL
from pymtl3_net.ocnlib.ifcs.packets import mk_mesh_pkt
from pymtl3_net.ocnlib.ifcs.positions import mk_mesh_pos
from pymtl3_net.ocnlib.utils import run_sim
from pymtl3_net.ocnlib.test.stream_sinks import NetSinkRTL as TestNetSinkRTL
from pymtl3_net.torusnet.DORYTorusRouteUnitRTL import DORYTorusRouteUnitRTL
from pymtl3_net.torusnet.RouteUnitDorFL import RouteUnitDorFL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, PktType, src_msgs, sink_msgs, ncols=2, nrows=2, pos_x=0, pos_y=0 ):

    outports = 5
    MeshPos = mk_mesh_pos( ncols, nrows )

    cmp_fn = lambda a, b : a.src_x == b.src_x and a.src_y == b.src_y and \
                               a.dst_y == b.dst_y and a.payload == b.payload


    s.src   = TestSrcRTL( PktType, src_msgs )
    s.dut   = DORYTorusRouteUnitRTL( PktType, MeshPos, ncols=ncols, nrows=nrows )
    s.sinks = [ TestNetSinkRTL( PktType, sink_msgs[i], cmp_fn=cmp_fn )
                for i in range ( outports ) ]

    # Connections
    s.src.send  //= s.dut.recv

    for i in range ( outports ):
      s.dut.send[i] //= s.sinks[i].recv

    s.dut.pos //= MeshPos( pos_x, pos_y )

  def done( s ):
    done = s.src.done()
    for x in s.sinks:
      done &= x.done()
    return done

  def line_trace( s ):
    return f"{s.dut.line_trace()}"

#-------------------------------------------------------------------------
# mk_dst_pkts
#-------------------------------------------------------------------------
# A helper function that computes destination packets using the FL model.

def mk_dst_pkts( pos_x, pos_y, ncols, nrows, src_pkts ):
  route_unit = RouteUnitDorFL( pos_x, pos_y, ncols, nrows, dimension='y' )
  return route_unit.route( src_pkts )

#=========================================================================
# Test cases
#=========================================================================
# TODO: Test DORX as well.

class RouteUnitDorRTL_Tests:

  @classmethod
  def setup_method( cls ):
    pass

  @pytest.mark.parametrize(
    'pos_x, pos_y',
    product( [ 0, 1, 2, 3 ], [ 0, 1, 2, 3 ] )
  )
  def test_simple_4x4( s, pos_x, pos_y, cmdline_opts ):

    ncols = 4
    nrows  = 4

    Pkt = mk_mesh_pkt( ncols, nrows, vc=2 )

    src_pkts = [
      #   src_x  y  dst_x  y  opq  vc  payload
      Pkt(    0, 0,     1, 1,   0,  0, 0xfaceb00c ),
      Pkt(    0, 0,     0, 0,   0,  0, 0xdeaddead ),
      Pkt(    0, 0,     1, 0,   0,  0, 0xdeadface ),
      Pkt(    0, 0,     3, 3,   0,  0, 0xdeadface ),
    ]
    dst_pkts = mk_dst_pkts( pos_x, pos_y, ncols, nrows, src_pkts )
    th = TestHarness( Pkt, src_pkts, dst_pkts, ncols, nrows, pos_x, pos_y )
    run_sim( th, cmdline_opts )
