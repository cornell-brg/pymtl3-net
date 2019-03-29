#=========================================================================
# MeshNetworkRTL_test.py
#=========================================================================
# Test for MeshNetworkRTL
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 20, 2019

import tempfile
from pymtl                   import *
from network.MeshNetworkRTL  import MeshNetworkRTL
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
def run_vector_test( model, test_vectors ):
 
  configs = configure_network()
  def tv_in( model, test_vector ):

    mesh_wid = 4
    mesh_ht  = 4
    MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )

    for i in range (configs.routers):
      model.pos_ports[i] = MeshPos( i%(configs.routers/configs.rows), i/(configs.routers/configs.rows) )
    if test_vector[0] != 'x':
      router_id = test_vector[0]
      pkt = mk_pkt( router_id%(configs.routers/configs.rows),
                  router_id/(configs.routers/configs.rows),
                  test_vector[1][0], test_vector[1][1], 1, test_vector[1][2])
    
      # Enable the network interface on specific router
      for i in range (configs.routers):
        model.recv_noc_ifc[i].en  = 0
      model.recv_noc_ifc[router_id].msg = pkt
      model.recv_noc_ifc[router_id].en  = 1

    for i in range (configs.routers):
      model.send_noc_ifc[i].rdy = 1

  def tv_out( model, test_vector ):
    if test_vector[2] != 'x':
      assert model.send_noc_ifc[test_vector[2]].msg.payload == test_vector[3]
#      assert 1 == 1
     
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()
  model.sim_reset()

def test_vector_MeshNetwork( dump_vcd, test_verilog ):

  configs = configure_network()
  model = MeshNetworkRTL()

  num_routers = configs.routers
  num_inports = configs.router_inports
  for r in range (num_routers):
    for i in range (num_inports):
      path = "top.routers[" + str(r) + "].input_units[" + str(i) + "].elaborate.QueueType"
      model.set_parameter(path, NormalQueueRTL)

  x = 'x'

  # Specific for wire connection (link delay = 0) in 2x2 Mesh topology
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

  # Specific for wire connection (link delay = 0) in 2x2 Mesh topology
  simple_4_4_test = [
#  router   [packet]   arr_router  msg 
  [  0,    [1,0,1001],     x,       x  ],
  [  0,    [1,1,1002],     x,       x  ],
  [  0,    [0,1,1003],     1,     1001 ],
  [  0,    [0,1,1004],     x,       x  ],
  [  0,    [1,0,1005],     4,     1003 ],
  ]
  run_vector_test( model, simple_4_4_test)

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( ComponentLevel6 ):

  def construct( s, MsgType, src_msgs, sink_msgs, src_initial,
                 src_interval, sink_initial, sink_interval,
                 arrival_time=None ):

    mesh_wid = 4
    mesh_ht  = 4

    MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )
    s.dut = MeshNetworkRTL()

    s.srcs  = [ TestSrcRTL   ( MsgType, src_msgs[i],  src_initial,  src_interval  )
              for i in range ( s.dut.num_routers ) ]
    s.sinks = [ TestSinkRTL  ( MsgType, sink_msgs[i], sink_initial,
              sink_interval, arrival_time[i]) for i in range ( s.dut.num_routers ) ]

    # Connections
    for i in range ( s.dut.num_routers ):
      s.connect( s.srcs[i].send,        s.dut.recv_noc_ifc[i] )
      s.connect( s.dut.send_noc_ifc[i], s.sinks[i].recv       )

    #TODO: provide pos for router...
    @s.update
    def up_pos():
      for x in range( s.dut.cols ):
        for y in range( s.dut.rows ):
          s.dut.pos_ports[y*s.dut.cols+x] = MeshPos( x, y )

    @s.update
    def up_idle_src_sink():
      for i in range ( 4 * ((s.dut.rows-2) * (s.dut.cols-2) + 4) ):
        s.dut.send[i].rdy = 0
        s.dut.recv[i].en  = 0
        s.dut.recv[i].msg = mk_pkt(0, 0, 0, 0, 0, 0)

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
# Test cases (specific for 4x4 mesh)
#-------------------------------------------------------------------------

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
arrival_pipes = [[8], [6], [6], [8],
                 [6], [4], [4], [6], 
                 [6], [4], [4], [6], 
                 [8], [6], [6], [8]]

def test_normal_simple():

  configs = configure_network()
  cols = configs.routers/configs.rows
  for (src, dst, payload) in test_msgs:
    pkt = mk_pkt( src%cols, src/cols, dst%cols, dst/cols, 1, payload )
    src_packets [src].append( pkt )
    sink_packets[dst].append( pkt )

  th = TestHarness( Packet, src_packets, sink_packets, 0, 0, 0, 0,
                    arrival_pipes )
  print "------------ test with source/sink --------------"
  run_sim( th )
