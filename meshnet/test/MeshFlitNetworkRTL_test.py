#=========================================================================
# MeshNetworkRTL_test.py
#=========================================================================
# Test for NetworkRTL
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 20, 2019

import tempfile
from pymtl3                           import *
from pymtl3.stdlib.rtl.queues         import NormalQueueRTL
from pymtl3.stdlib.test.test_srcs     import TestSrcRTL
from ocn_pclib.test.net_sinks         import TestNetSinkRTL
from pymtl3.stdlib.test               import TestVectorSimulator
from meshnet.MeshFlitNetworkRTL       import MeshFlitNetworkRTL
from meshnet.MeshFlitNetworkRTL       import MeshFlitNetworkRTL
from meshnet.DORYMeshRouteUnitRTL     import DORYMeshRouteUnitRTL
from meshnet.DORXMeshRouteUnitRTL     import DORXMeshRouteUnitRTL
from meshnet.TestMeshRouteUnitRTL     import TestMeshRouteUnitRTL
from router.InputUnitRTL              import InputUnitRTL
from ocn_pclib.ifcs.positions         import mk_mesh_pos
from ocn_pclib.ifcs.packets           import mk_mesh_pkt
from ocn_pclib.ifcs.flits             import mk_mesh_flit, flitisize_mesh_flit
from pymtl3.passes.sverilog           import ImportPass, TranslationPass
from pymtl3.passes                    import DynamicSim
from meshnet.DORYMeshFlitRouteUnitRTL import DORYMeshFlitRouteUnitRTL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, MsgType, mesh_wid, mesh_ht, src_msgs, sink_msgs, 
                 src_initial, src_interval, sink_initial, sink_interval,
                 arrival_time=None ):

    MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )
    s.num_routers = mesh_wid * mesh_ht
    s.dut = MeshFlitNetworkRTL( MsgType, MeshPos, mesh_wid, mesh_ht, 0)
    match_func = lambda a, b : a.payload == b.payload

    s.srcs  = [ TestSrcRTL   ( MsgType, src_msgs[i],  src_initial,  src_interval  )
              for i in range ( s.dut.num_routers ) ]
    if arrival_time != None:
      s.sinks = [ TestNetSinkRTL  ( MsgType, sink_msgs[i], sink_initial,
                sink_interval, arrival_time[i], match_func=match_func) 
                for i in range ( s.dut.num_routers ) ]
    else:
      s.sinks = [ TestNetSinkRTL  ( MsgType, sink_msgs[i], sink_initial,
                sink_interval, match_func=match_func) 
                for i in range ( s.dut.num_routers ) ]

    # Connections
    for i in range ( s.dut.num_routers ):
      s.connect( s.srcs[i].send, s.dut.recv[i]   )
      s.connect( s.dut.send[i],  s.sinks[i].recv )

    #TODO: provide pos for router...
    XYType = mk_bits( clog2( mesh_wid ) )
    @s.update
    def up_pos():
      for y in range( mesh_ht ):
        for x in range( mesh_wid ):
          idx = y * mesh_wid + x
          s.dut.pos_x[idx] = XYType(x)
          s.dut.pos_y[idx] = XYType(y)

  def done( s ):
    srcs_done = 1
    sinks_done = 1
    for i in range( s.num_routers ):
      if s.srcs[i].done() == 0:
        srcs_done = 0
    for i in range( s.num_routers ):
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

  test_harness.elaborate()
#  test_harness.dut.sverilog_translate = True
#  test_harness.dut.sverilog_import = True
#  test_harness.apply( TranslationPass() )
#  test_harness = ImportPass()( test_harness )
  test_harness.apply( SimpleSim )
#  test_harness.apply( DynamicSim )
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

def test_srcsink_mesh2x2_flit():

  mesh_wid = mesh_ht = 2

  opaque_nbits = 1
  nvcs = 1
  payload_nbits = 32

  flit_size = 16

  PacketType = mk_mesh_pkt( mesh_wid, mesh_ht, opaque_nbits, nvcs, payload_nbits )
  FlitType = mk_mesh_flit( mesh_wid, mesh_ht, 0,
                 opaque_nbits, total_flit_nbits=flit_size, nvcs=nvcs )
#  pkt = mk_pkt( 0, 0, 1, 1, 0, 0xfaceb00c )
  pkt  = PacketType( 0, 0, 1, 1, 0, 0xface )
  flits = flitisize_mesh_flit( pkt, mesh_wid, mesh_ht,
          opaque_nbits, nvcs, payload_nbits, flit_size )

  src_packets  = [ flits, [], [], [] ]
  sink_packets = [ [], [], [], flits ]

  th = TestHarness( FlitType, 2, 2, src_packets, sink_packets, 0, 0, 0, 0 )
  th.set_param( "top.dut.routers*.construct", RouteUnitType=DORYMeshFlitRouteUnitRTL )
  run_sim( th )

