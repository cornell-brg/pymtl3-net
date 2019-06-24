#=========================================================================
# RingNetworkRTL_test.py
#=========================================================================
# Test for RingNetworkRTL
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 20, 2019

from pymtl3 import *

from pymtl3.stdlib.test.test_srcs import TestSrcRTL
from ocn_pclib.test.net_sinks import TestNetSinkRTL

from ocn_pclib.ifcs.packets   import mk_ring_pkt
from ocn_pclib.ifcs.positions import mk_ring_pos
from ringnet.RingNetworkRTL import RingNetworkRTL

from copy import deepcopy

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness( Component ):

  def construct( s, MsgType, num_routers, src_msgs, sink_msgs ):

    RingPos = mk_ring_pos( num_routers )
    s.dut = RingNetworkRTL( MsgType, RingPos, num_routers, 0)

    s.srcs  = [ TestSrcRTL   ( MsgType, src_msgs[i] )
              for i in range ( s.dut.num_routers ) ]
    s.sinks = [ TestNetSinkRTL  ( MsgType, sink_msgs[i] ) for i in range ( s.dut.num_routers ) ]

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
# Test cases (specific for 4x4 mesh)
#-------------------------------------------------------------------------

def test_srcsink_torus4x4():

  #           src, dst, payload
  test_msgs = [ (0, 15, 101), (1, 14, 102), (2, 13, 103), (3, 12, 104),
                (4, 11, 105), (5, 10, 106), (6,  9, 107), (7,  8, 108),
                (8,  7, 109), (9,  6, 110), (10, 5, 111), (11, 4, 112),
                (12, 3, 113), (13, 2, 114), (14, 1, 115), (15, 0, 116),
                (7,  9, 99),  (8,  9, 98),  (6,  9, 97) ]

  src_packets  =  [ [],[],[],[],
                    [],[],[],[],
                    [],[],[],[],
                    [],[],[],[] ]

  sink_packets =  [ [],[],[],[],
                    [],[],[],[],
                    [],[],[],[],
                    [],[],[],[] ]

  num_routers = 16
  PktType = mk_ring_pkt( num_routers )

  for (src, dst, payload) in test_msgs:
    pkt = PktType( src, dst, 1, 0, payload )
#    flits = flitisize_ring_flit( pkt, 1, num_routers )
    src_packets [src].append( pkt )
    sink_pkt = deepcopy( pkt )
    if abs(dst - src) > num_routers/2:
      sink_pkt.vc_id = 1
    sink_packets[dst].append( sink_pkt )

  th = TestHarness( PktType, num_routers, src_packets, sink_packets )
#                    0, 0, 0, 0, arrival_pipes )

  th.set_param( 'top.dut.routers*.route_units*.construct', num_routers = num_routers )
#  num_inports = 3
#  for r in range ( num_routers ):
#    for i in range (num_inports):
#      path_ru_nr = "top.dut.routers[" + str(r) + "].route_units[" + str(i) + "].elaborate.num_routers"
#      path_qt      = "top.dut.routers[" + str(r) + "].input_units[" + str(i) + "].elaborate.QueueType"
#      th.set_parameter(path_qt,    NormalQueueRTL)
#      th.set_parameter(path_ru_nr, num_routers )

  run_sim( th )

