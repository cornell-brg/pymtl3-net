"""
=========================================================================
CMeshNetworkRTL_test.py
=========================================================================
Test for CMeshNetworkRTL

Author : Cheng Tan, Yanghui Ou
  Date : April 16, 2019
"""

import itertools
import pytest
import random
import tempfile
from pymtl3                         import *
from meshnet.MeshNetworkRTL         import MeshNetworkRTL
from cmeshnet.CMeshNetworkRTL       import CMeshNetworkRTL
from pymtl3.stdlib.rtl.queues       import NormalQueueRTL
from pymtl3.stdlib.test.test_srcs   import TestSrcRTL
from ocn_pclib.test.net_sinks       import TestNetSinkRTL
from pymtl3.stdlib.test             import TestVectorSimulator
from ocn_pclib.ifcs.packets         import *
from ocn_pclib.ifcs.positions       import *
from meshnet.DORYMeshRouteUnitRTL   import DORYMeshRouteUnitRTL
from meshnet.DORXMeshRouteUnitRTL   import DORXMeshRouteUnitRTL
from cmeshnet.DORXCMeshRouteUnitRTL import DORXCMeshRouteUnitRTL
from cmeshnet.DORYCMeshRouteUnitRTL import DORYCMeshRouteUnitRTL

#-------------------------------------------------------------------------
# Test Vector
#-------------------------------------------------------------------------
def run_vector_test( model, PacketType, test_vectors, ncols, nrows ):

  def tv_in( model, test_vector ):
    num_routers = ncols * nrows
    MeshPos = mk_mesh_pos( ncols, nrows )

    if test_vector[0] != 'x':
      router_id = test_vector[0]
      pkt = PacketType( router_id % ncols, router_id / ncols,
            test_vector[1][0], test_vector[1][1], test_vector[2], 1,
            test_vector[1][2] )

      # Enable the network interface on specific router
      for i in range (num_routers):
        model.recv[i].en  = 0
      model.recv[router_id].msg = pkt
      model.recv[router_id].en  = 1

    for i in range (num_routers*4):
      model.send[i].rdy = 1

  def tv_out( model, test_vector ):
    if test_vector[3] != 'x':
      assert model.send[test_vector[3]*4].msg.payload == test_vector[4]

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()
  model.sim_reset()

def test_vector_mesh2x2( dump_vcd, test_verilog ):

  ncols = 2
  nrows  = 2
  inports = outports = 8
  MeshPos = mk_mesh_pos( ncols, nrows )
  PacketType = mk_cmesh_pkt( ncols, nrows, inports, outports )
  model = CMeshNetworkRTL( PacketType, MeshPos, ncols, nrows, 4, 0 )

#  num_routers = ncols * nrows * 4
#  num_inports = 8
#  for r in range (num_routers):
#    for i in range (num_inports):
#      path_qt = "top.routers[" + str(r) + "].input_units[" + str(i) + "].elaborate.QueueType"
#      path_ru = "top.routers[" + str(r) + "].elaborate.RouteUnitType"
#      model.set_parameter(path_qt, NormalQueueRTL)
#      model.set_parameter(path_ru, DORXMeshRouteUnitRTL)

  x = 'x'

  # Specific for wire connection (link delay = 0) in 2x2 Mesh topology
  simple_2_2_test = [
#  router   [packet]    tmnl ar_router  msg
  [  0,    [1,0,1001],    0,    x,       x  ],
  [  0,    [1,1,1002],    0,    x,       x  ],
  [  0,    [0,1,1003],    0,    1,     1001 ],
  [  0,    [0,1,1004],    0,    x,       x  ],
  [  0,    [1,0,1005],    0,    2,     1003 ],
  [  2,    [0,0,1006],    0,    2,     1004 ],
  [  1,    [0,1,1007],    0,    1,     1005 ],
  [  2,    [1,1,1008],    0,    x,       x  ],
  ]

  run_vector_test( model, PacketType, simple_2_2_test, ncols, nrows)

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, MsgType, ncols, nrows, src_msgs, sink_msgs,
                 src_initial, src_interval, sink_initial, sink_interval,
                 arrival_time=None ):

    MeshPos = mk_mesh_pos( ncols, nrows )
    s.dut = CMeshNetworkRTL( MsgType, MeshPos, ncols, nrows, 2, 0)
    match_func = lambda a, b : a.payload == b.payload and a.dst_x == b.dst_x and\
                               a.dst_y == b.dst_y

    s.srcs  = [ TestSrcRTL   ( MsgType, src_msgs[i],  src_initial,  src_interval  )
              for i in range ( s.dut.num_terminals ) ]
    s.sinks = [ TestNetSinkRTL  ( MsgType, sink_msgs[i], sink_initial,
                sink_interval, match_func=match_func)
                for i in range ( s.dut.num_terminals ) ]

    # Connections
    for i in range ( s.dut.num_terminals ):
      s.srcs[i].send //= s.dut.recv[i]
      s.dut.send[i]  //= s.sinks[i].recv

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

def run_sim( test_harness, max_cycles=1000 ):

  # Create a simulator

  test_harness.apply( SimpleSim )
  test_harness.sim_reset()

  # Run simulation

  ncycles = 0
  print()
  print( "{}:{}".format( ncycles, test_harness.line_trace() ))
  while not test_harness.done() and ncycles < max_cycles:
    test_harness.tick()
    ncycles += 1
    print( "{}:{}".format( ncycles, test_harness.line_trace() ))

  # Check timeout

  assert ncycles < max_cycles

  test_harness.tick()
  test_harness.tick()
  test_harness.tick()

#-------------------------------------------------------------------------
# Test cases (specific for 2x2 cmesh)
#-------------------------------------------------------------------------

def test_srcsink_mesh2x2():

  ncols = nrows = 2
  inports = outports = 6

  opaque_nbits = 1
  vc = 1
  payload_nbits = 32

  PacketType = mk_cmesh_pkt(  ncols, nrows, inports, outports,
                              opaque_nbits, vc, payload_nbits )
  pkt = PacketType( 0, 0, 1, 1, 1, 0, 0xface )

  src_packets  = [ [pkt], [], [], [], [], [], [], [] ]
  sink_packets = [ [], [], [], [], [], [], [], [pkt] ]

  th = TestHarness( PacketType, 2, 2, src_packets, sink_packets, 0, 0, 0, 0 )

  run_sim( th )

#-------------------------------------------------------------------------
# Test cases random simple
#-------------------------------------------------------------------------

@pytest.mark.parametrize(
  "ncols, nrows, nports",
  list(itertools.product(
    # list(range(2, 8)),
    # list(range(2, 8)),
    # list(range(4, 10, 2)),
    [2, 4],
    [2, 4],
    [6],
  ))
)
def test_srcsink_random_simple( ncols, nrows, nports ):
  n_pkts = 3
  inports = outports = nports
  node_per_cnode = nports - 4
  opaque_nbits = 1
  vc = 1
  payload_nbits = 32

  PacketType = mk_cmesh_pkt(  ncols, nrows, inports, outports,
                              opaque_nbits, vc, payload_nbits )

  # src_x y, dst_x y, dst_ter, opq, payload
  pkts = [PacketType(random.randint(0, ncols-1), \
                     random.randint(0, nrows-1), \
                     random.randint(0, ncols-1), \
                     random.randint(0, nrows-1), \
                     random.randint(0, node_per_cnode-1),  \
                     random.randint(0, 2**opaque_nbits-1), \
                     random.randint(0, 2**32-1)) for _ in range(n_pkts)]
  src_packets  = [[] for _ in range(ncols * nrows * node_per_cnode)]
  sink_packets = [[] for _ in range(ncols * nrows * node_per_cnode)]

  for pkt in pkts:
    # Assuming always using the first node in a concentrated node
    src_idx  = (int(pkt.src_y) * ncols + int(pkt.src_x)) * node_per_cnode
    sink_idx = (int(pkt.dst_y) * ncols + int(pkt.dst_x)) * node_per_cnode + int(pkt.dst_ter)
    src_packets[src_idx].append(pkt)
    sink_packets[sink_idx].append(pkt)

  th = TestHarness( PacketType, ncols, nrows, src_packets, sink_packets, 0, 0, 0, 0 )

  run_sim( th )
