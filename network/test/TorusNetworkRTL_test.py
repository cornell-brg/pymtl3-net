#=========================================================================
# TorusNetworkRTL_test.py
#=========================================================================
# Test for TorusNetworkRTL
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 20, 2019

import tempfile
from pymtl                   import *
from network.TorusNetworkRTL import TorusNetworkRTL
from ocn_pclib.rtl.queues    import NormalQueueRTL
from pclib.test.test_srcs    import TestSrcRTL
from pclib.test.test_sinks   import TestSinkRTL
from pclib.test              import TestVectorSimulator
from ocn_pclib.ifcs.Packet   import Packet, mk_pkt
from ocn_pclib.ifcs.Position import *
from Configs                 import configure_network

#-------------------------------------------------------------------------
# Test Vector
#-------------------------------------------------------------------------

def run_vector_test( model, test_vectors, mesh_wid, mesh_ht ):
 
  def tv_in( model, test_vector ):

    num_routers = mesh_wid * mesh_ht
    MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )

    if test_vector[0] != 'x':
      router_id = test_vector[0]
      pkt = mk_pkt( router_id % mesh_wid, router_id / mesh_wid,
                  test_vector[1][0], test_vector[1][1], 1, test_vector[1][2])
    
      # Enable the network interface on specific router
      for i in range (num_routers):
        model.recv[i].en  = 0
      model.recv[router_id].msg = pkt
      model.recv[router_id].en  = 1

    for i in range (num_routers):
      model.send[i].rdy = 1

  def tv_out( model, test_vector ):
    if test_vector[2] != 'x':
      assert model.send[test_vector[2]].msg.payload == test_vector[3]
     
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()
  model.sim_reset()

def test_vector_Torus2x2( dump_vcd, test_verilog ):

  mesh_wid = 2
  mesh_ht  = 2
  MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )
  model = TorusNetworkRTL( Packet, MeshPos, mesh_wid, mesh_ht, 0 )

  num_routers = mesh_wid * mesh_ht
  num_inports = 5
  for r in range (num_routers):

    for i in range (num_inports):
      path_ru_cols = "top.routers[" + str(r) + "].route_units[" + str(i) + "].elaborate.cols"
      path_ru_rows = "top.routers[" + str(r) + "].route_units[" + str(i) + "].elaborate.rows"
      path_qt = "top.routers[" + str(r) + "].input_units[" + str(i) + "].elaborate.QueueType"
      model.set_parameter(path_qt,      NormalQueueRTL)
      model.set_parameter(path_ru_cols, mesh_wid)
      model.set_parameter(path_ru_rows, mesh_ht )

  x = 'x'

  # Specific for wire connection (link delay = 0) in 2x2 Torus topology
  simple_2_2_test = [
#  router   [packet]   arr_router  msg 
  [  0,    [1,0,1001],     x,       x  ],
  [  0,    [1,1,1002],     x,       x  ],
  [  0,    [0,1,1003],     1,     1001 ],
  [  0,    [0,1,1004],     x,       x  ],
  [  0,    [1,0,1005],     2,     1003 ],
  [  2,    [0,0,1006],     x,       x  ],
  [  1,    [0,1,1007],     1,     1005 ],
  [  2,    [1,1,1008],     0,     1006 ],
  [  x,    [0,0,0000],     x,       x  ],
  [  x,    [0,0,0000],     2,     1007 ],
  [  x,    [0,0,0000],     x,       x  ],
  [  x,    [0,0,0000],     3,     1008 ],
  [  x,    [0,0,0000],     x,       x  ],
  [  x,    [0,0,0000],     x,       x  ],
  [  x,    [0,0,0000],     x,       x  ],
  [  x,    [0,0,0000],     x,       x  ],
  ]

  print "------------ test with test vector for torus 2x2 --------------"
  run_vector_test( model, simple_2_2_test, mesh_wid, mesh_ht)

def test_vector_Torus4x4( dump_vcd, test_verilog ):

  mesh_wid = 4
  mesh_ht  = 4
  MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )
  model = TorusNetworkRTL( Packet, MeshPos, mesh_wid, mesh_ht, 0)

  num_routers = mesh_wid * mesh_ht
  num_inports = 5
  for r in range (num_routers):
    for i in range (num_inports):
      path_ru_cols = "top.routers[" + str(r) + "].route_units[" + str(i) + "].elaborate.cols"
      path_ru_rows = "top.routers[" + str(r) + "].route_units[" + str(i) + "].elaborate.rows"
      path_qt = "top.routers[" + str(r) + "].input_units[" + str(i) + "].elaborate.QueueType"
      model.set_parameter(path_qt,      NormalQueueRTL)
      model.set_parameter(path_ru_cols, mesh_wid)
      model.set_parameter(path_ru_rows, mesh_ht )

  x = 'x'
  # Specific for wire connection (link delay = 0) in 4x4 Torus topology
  simple_4_4_test = [
#  router   [packet]   arr_router  msg
  [  0,    [1,0,1001],     x,       x  ],
  [  0,    [1,1,1002],     x,       x  ],
  [  0,    [0,1,1003],     1,     1001 ],
  [  0,    [0,1,1004],     x,       x  ],
  [  0,    [1,0,1005],     4,     1003 ],
  ]

  print "------------ test with test vector for torus 4x4 --------------"
  run_vector_test( model, simple_4_4_test, mesh_wid, mesh_ht)

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness( ComponentLevel6 ):

  def construct( s, MsgType, mesh_wid, mesh_ht, src_msgs, sink_msgs,
                 src_initial, src_interval, sink_initial, sink_interval,
                 arrival_time=None ):

    MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )
    s.dut = TorusNetworkRTL( MsgType, MeshPos, mesh_wid, mesh_ht, 0)

    s.srcs  = [ TestSrcRTL   ( MsgType, src_msgs[i],  src_initial,  src_interval  )
              for i in range ( s.dut.num_routers ) ]
    s.sinks = [ TestSinkRTL  ( MsgType, sink_msgs[i], sink_initial,
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

  num_inports = 5
  for r in range (mesh_wid * mesh_ht):
    for i in range (num_inports):
      path_ru_cols = "top.dut.routers[" + str(r) + "].route_units[" + str(i) + "].elaborate.cols"
      path_ru_rows = "top.dut.routers[" + str(r) + "].route_units[" + str(i) + "].elaborate.rows"
      path_qt      = "top.dut.routers[" + str(r) + "].input_units[" + str(i) + "].elaborate.QueueType"
      th.set_parameter(path_qt,      NormalQueueRTL)
      th.set_parameter(path_ru_cols, mesh_wid)
      th.set_parameter(path_ru_rows, mesh_ht )


  print "------------ test with source/sink for torus 4x4 --------------"
  run_sim( th )

