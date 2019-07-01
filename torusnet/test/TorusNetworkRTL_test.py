#=========================================================================
# TorusNetworkRTL_test.py
#=========================================================================
# Test for TorusNetworkRTL
#
# Author : Yanghui Ou, Cheng Tan
#   Date : July 1, 2019

from pymtl3 import *
from pymtl3.stdlib.test.test_srcs import TestSrcRTL
from ocn_pclib.test.net_sinks import TestNetSinkRTL
from ocn_pclib.ifcs.packets import mk_mesh_pkt
from ocn_pclib.ifcs.positions import mk_mesh_pos
from torusnet.TorusNetworkRTL import TorusNetworkRTL
from torusnet.TorusNetworkFL import torusnet_fl

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, PktType, ncols, nrows, src_msgs, sink_msgs ):

    s.nrouters = ncols * nrows
    MeshPos = mk_mesh_pos( ncols, nrows )
    match_func = lambda a, b : a.src_x == b.src_x and a.src_y == b.src_y and \
                               a.dst_y == b.dst_y and a.payload == b.payload

    s.srcs  = [ TestSrcRTL   ( PktType, src_msgs[i] )
                for i in range ( s.nrouters ) ]
    s.dut   = TorusNetworkRTL( PktType, MeshPos, ncols, nrows, 0)
    s.sinks = [ TestNetSinkRTL  ( PktType, sink_msgs[i], match_func=match_func )
                for i in range ( s.nrouters ) ]

    # Connections
    for i in range ( s.nrouters ):
      s.connect( s.srcs[i].send, s.dut.recv[i]   )
      s.connect( s.dut.send[i],  s.sinks[i].recv )

  def done( s ):
    srcs_done  = True
    sinks_done = True
    for i in range( s.nrouters ):
      if not s.srcs[i].done():
        srcs_done = False
        break
      if not s.sinks[i].done() == 0:
        sinks_done = False
        break
    return srcs_done and sinks_done

  def line_trace( s ):
    return s.dut.line_trace()

#-------------------------------------------------------------------------
# mk_src_pkts
#-------------------------------------------------------------------------

def mk_src_pkts( nrows, ncols, lst ):
  nterminals = nrows * ncols
  src_pkts = [ [] for _ in range( nterminals ) ]
  for pkt in lst:
    src_id = int(pkt.src_x) + int(pkt.src_y) * ncols
    src_pkts[ src_id ].append( pkt )
  return src_pkts

#=========================================================================
# Test cases
#=========================================================================

class Ringnet_Tests( object ):

  def run_sim( s, th, max_cycles=200 ):
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
    ncols = 2
    nrows = 2

    Pkt = mk_mesh_pkt( ncols, nrows, nvcs=2 )

    src_pkts = mk_src_pkts( ncols, nrows, [
      #    src_x  y  dst_x  y   opq vc payload
      Pkt(     0, 0,     1, 1,  0,  0, 0xfaceb00c ),
    ])
    dst_pkts = torusnet_fl( ncols, nrows, src_pkts )
    th = TestHarness( Pkt, ncols, nrows, src_pkts, dst_pkts )
    s.run_sim( th )
