#=========================================================================
# CMeshFlitNetworkRTL_test.py
#=========================================================================
# Test for CMeshFlitNetworkRTL
#
# Author : Cheng Tan
#   Date : July 20, 2019

import tempfile
from pymtl3                             import *
from meshnet.MeshNetworkRTL             import MeshNetworkRTL
from cmeshnet.CMeshFlitNetworkRTL       import CMeshFlitNetworkRTL
from pymtl3.stdlib.rtl.queues           import NormalQueueRTL
from pymtl3.stdlib.test.test_srcs       import TestSrcRTL
from ocn_pclib.test.net_sinks           import TestNetSinkRTL
from pymtl3.stdlib.test                 import TestVectorSimulator
from ocn_pclib.ifcs.packets             import *
from ocn_pclib.ifcs.flits               import *
from ocn_pclib.ifcs.positions           import *
from meshnet.DORYMeshRouteUnitRTL       import DORYMeshRouteUnitRTL
from meshnet.DORXMeshRouteUnitRTL       import DORXMeshRouteUnitRTL
from cmeshnet.DORXCMeshRouteUnitRTL     import DORXCMeshRouteUnitRTL
from cmeshnet.DORYCMeshRouteUnitRTL     import DORYCMeshRouteUnitRTL
from cmeshnet.DORYCMeshFlitRouteUnitRTL import DORYCMeshFlitRouteUnitRTL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, MsgType, mesh_wid, mesh_ht, src_msgs, sink_msgs, 
                 src_initial, src_interval, sink_initial, sink_interval,
                 arrival_time=None ):

    MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )
    s.dut = CMeshFlitNetworkRTL( MsgType, MeshPos, mesh_wid, mesh_ht, 2, 0)
    match_func = lambda a, b : a.payload == b.payload

    s.srcs  = [ TestSrcRTL   ( MsgType, src_msgs[i],  src_initial,  src_interval  )
              for i in range ( s.dut.num_terminals ) ]
    s.sinks = [ TestNetSinkRTL  ( MsgType, sink_msgs[i], sink_initial,
                sink_interval, match_func=match_func) 
                for i in range ( s.dut.num_terminals ) ]

    # Connections
    for i in range ( s.dut.num_terminals ):
      s.connect( s.srcs[i].send, s.dut.recv[i]   )
      s.connect( s.dut.send[i],  s.sinks[i].recv )

  def done( s ):
    srcs_done = 1
    sinks_done = 1
    for i in range( s.dut.num_routers ):
      if s.srcs[i].done() == 0:
        srcs_done = 0
    for i in range( s.dut.num_routers ):
      if s.sinks[i].done() == 0:
        sinks_done = 0
    return srcs_done and sinks_done
  def line_trace( s ):
    return s.dut.line_trace()

#-------------------------------------------------------------------------
# run_rtl_sim
#-------------------------------------------------------------------------

def run_sim( test_harness, max_cycles=100 ):

  # Create a simulator

  test_harness.apply( SimpleSim )
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
# Test cases (specific for 2x2 cmesh)
#-------------------------------------------------------------------------

def test_srcsink_mesh2x2():

  mesh_wid = mesh_ht = 2
  inports = outports = 6

  opaque_nbits = 1
  nvcs = 1
  payload_nbits = 32
  flit_size = 8

  PacketType = mk_cmesh_pkt(  mesh_wid, mesh_ht, inports, outports,
                              opaque_nbits, nvcs, payload_nbits )
  FlitType   = mk_cmesh_flit( mesh_wid, mesh_ht, inports, outports, 0,
                              opaque_nbits, total_flit_nbits=flit_size, nvcs=nvcs )
  pkt = PacketType( 0, 0, 1, 1, 1, 0, 0xface )
  flits = flitisize_cmesh_flit( pkt, mesh_wid, mesh_ht, inports, outports,
          opaque_nbits, nvcs, payload_nbits, flit_size )

  src_packets  = [ flits, [], [], [], [], [], [], [] ]
  sink_packets = [ [], [], [], [], [], [], [], flits ]

  th = TestHarness( FlitType, 2, 2, src_packets, sink_packets, 0, 0, 0, 0 )

  run_sim( th )
