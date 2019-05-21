#=========================================================================
# TorusNetworkCL_test.py
#=========================================================================
# Test for TorusNetworkCL
#
# Author : Cheng Tan
#   Date : May 20, 2019

import tempfile
from pymtl                         import *
from torusnet.TorusNetworkCL       import TorusNetworkCL
from ocn_pclib.rtl.queues          import NormalQueueRTL
from pclib.test.test_srcs          import TestSrcCL
from ocn_pclib.test.net_sinks      import TestNetSinkCL
from pclib.test                    import TestVectorSimulator
from ocn_pclib.ifcs.Packet         import Packet, mk_pkt
from ocn_pclib.ifcs.Position       import *
from torusnet.DORYTorusRouteUnitCL import DORYTorusRouteUnitCL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness( Component ):

  def construct( s, MsgType, mesh_wid, mesh_ht, src_msgs, sink_msgs,
                 src_initial, src_interval, sink_initial, sink_interval,
                 arrival_time=None ):

    MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )
    s.dut = TorusNetworkCL( MsgType, MeshPos, mesh_wid, mesh_ht, 0)

    s.srcs  = [ TestSrcCL   ( src_msgs[i],  src_initial,  src_interval  )
              for i in range ( s.dut.num_routers ) ]
    s.sinks = [ TestNetSinkCL  ( sink_msgs[i], sink_initial,
              sink_interval, arrival_time[i]) for i in range ( s.dut.num_routers ) ]

    # Connections
    for i in range ( s.dut.num_routers ):
      s.connect( s.srcs[i].send, s.dut.recv[i]   )
      s.connect( s.dut.send[i],  s.sinks[i].recv )

  def done( s ):
    srcs_done = 1
    sinks_done = 1
    for i in range( s.dut.num_routers ):
      if s.srcs[i].done() == 0:
        srcs_done = 0
        break
      if s.sinks[i].done() == 0:
        sinks_done = 0
        break
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
# Test cases (specific for 4x4 mesh)
#-------------------------------------------------------------------------

def test_srcsink_torus4x4():

  #           src, dst, payload
  test_msgs = [ (0, 15, 101), (1, 14, 102), (2, 13, 103), (3, 12, 104),
                (4, 11, 105), (5, 10, 106), (6,  9, 107), (7,  8, 108),
                (8,  7, 109), (9,  6, 110), (10, 5, 111), (11, 4, 112),
                (12, 3, 113), (13, 2, 114), (14, 1, 115), (15, 0, 116) ]
  
  src_packets  =  [ [],[],[],[],
                    [],[],[],[],
                    [],[],[],[],
                    [],[],[],[] ]
  
  sink_packets =  [ [],[],[],[],
                    [],[],[],[],
                    [],[],[],[],
                    [],[],[],[] ]
  
  # note that need to yield one/two cycle for reset
  arrival_pipes = [[4], [4], [4], [4],
                   [4], [4], [4], [4],
                   [4], [4], [4], [4],
                   [4], [4], [4], [4]]
  
  mesh_wid = 4
  mesh_ht  = 4
  for (src, dst, payload) in test_msgs:
    pkt = mk_pkt( src%mesh_wid, src/mesh_wid, dst%mesh_wid, dst/mesh_wid, 1, payload )
    src_packets [src].append( pkt )
    sink_packets[dst].append( pkt )

  th = TestHarness( Packet, mesh_wid, mesh_ht, src_packets, sink_packets, 
                    0, 0, 0, 0, arrival_pipes )

  run_sim( th )

