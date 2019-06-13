#=========================================================================
# BflyNetworkRTL_test.py
#=========================================================================
# Test for BflyNetworkRTL
#
# Author : Cheng Tan, Yanghui Ou
#   Date : April 8, 2019

import tempfile
from pymtl3                        import *
from pymtl3.stdlib.rtl.queues      import NormalQueueRTL
from pymtl3.stdlib.test.test_srcs  import TestSrcRTL
from pymtl3.stdlib.test.test_sinks import TestSinkRTL
from pymtl3.stdlib.test            import TestVectorSimulator
from bflynet.BflyNetworkRTL        import BflyNetworkRTL
from ocn_pclib.ifcs.packets        import *
from ocn_pclib.ifcs.positions      import *

#-------------------------------------------------------------------------
# Test Vector
#-------------------------------------------------------------------------

def run_vector_test( model, test_vectors, k_ary, n_fly ):
 
  def tv_in( model, test_vector ):

    num_routers   = n_fly * ( k_ary ** ( n_fly - 1 ) )
    num_terminals = k_ary * ( k_ary ** ( n_fly - 1 ) )
    r_rows        = k_ary ** ( n_fly - 1 )
    BfPos         = mk_bf_pos( r_rows, n_fly )

    if test_vector[0] != 'x':
      terminal_id = test_vector[0]
      pkt = mk_bf_pkt( terminal_id, test_vector[1][0], k_ary, n_fly, 1, test_vector[1][1])
    
      # Enable the network interface on specific router
      for i in range (num_terminals):
        model.recv[i].en  = 0
      model.recv[terminal_id].msg = pkt
      model.recv[terminal_id].en  = 1

    for i in range (num_terminals):
      model.send[i].rdy = 1

  def tv_out( model, test_vector ):
    if test_vector[2] != 'x':
      assert model.send[test_vector[2]].msg.payload == test_vector[3]
     
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()
  model.sim_reset()

def test_vector_Bf2( dump_vcd, test_verilog ):

  k_ary = 2
  n_fly = 1
  num_routers = n_fly * ( k_ary ** ( n_fly - 1 ) )
  r_rows      = k_ary ** ( n_fly - 1 )
  BfPos = mk_bf_pos( r_rows, n_fly )
  model = BflyNetworkRTL( BfPacket, BfPos, k_ary, n_fly, 0 )

  for r in range (num_routers):
    path_k = "top.routers[" + str(r) + "].elaborate.k_ary"
    model.set_parameter(path_k, k_ary)
    for i in range (k_ary):
      path_qt = "top.routers[" + str(r) + "].input_units[" + str(i) + "].elaborate.QueueType"
      path_nf = "top.routers[" + str(r) + "].route_units[" + str(i) + "].elaborate.n_fly"
      model.set_parameter(path_qt, NormalQueueRTL)
      model.set_parameter(path_nf, n_fly)

  x = 'x'

  # Specific for wire connection (link delay = 0) in 2x2 Torus topology
  simple_2_test = [
# terminal [packet]   arr_term   msg 
  [  0,    [0,1001],     x,       x  ],
  [  0,    [1,1002],     0,     1001 ],
  [  0,    [1,1003],     1,     1002 ],
  [  0,    [1,1004],     1,     1003 ],
  [  0,    [0,1005],     1,     1004 ],
  [  x,    [0,0000],     1,     1005 ],
  [  x,    [0,0000],     x,       x  ],
  [  x,    [0,0000],     x,       x  ],
  [  x,    [0,0000],     x,       x  ],
  [  x,    [0,0000],     x,       x  ],
  [  x,    [0,0000],     x,       x  ],
  [  x,    [0,0000],     x,       x  ],
  ]

  run_vector_test( model, simple_2_test, k_ary, n_fly)

def test_vector_Bf4( dump_vcd, test_verilog ):

  k_ary = 2
  n_fly = 2
  num_routers  = n_fly * ( k_ary ** ( n_fly - 1 ) )
  r_rows = k_ary ** ( n_fly - 1 )
  BfPos = mk_bf_pos( r_rows, n_fly )

  model = BflyNetworkRTL( BfPacket, BfPos, k_ary, n_fly, 0 )

  for r in range (num_routers):
    path_k = "top.routers[" + str(r) + "].elaborate.k_ary"
    model.set_parameter(path_k, k_ary)
    for i in range (k_ary):
      path_qt = "top.routers[" + str(r) + "].input_units[" + str(i) + "].elaborate.QueueType"
      path_nf = "top.routers[" + str(r) + "].route_units[" + str(i) + "].elaborate.n_fly"
      model.set_parameter(path_qt, NormalQueueRTL)
      model.set_parameter(path_nf, n_fly)

  x = 'x'
  # Specific for wire connection (link delay = 0) in 4x4 Torus topology
  simple_4_test = [
# terminal [packet]   arr_term   msg
  [  0,    [0,1001],     x,       x  ],
  [  0,    [2,1002],     x,       x  ],
  [  0,    [3,1003],     0,     1001 ],
  [  x,    [0,0000],     2,     1002 ],
  [  0,    [1,1004],     3,     1003 ],
  [  0,    [0,1005],     x,       x  ],
  [  x,    [0,0000],     1,     1004 ],
  [  x,    [0,0000],     0,     1005 ],
  ]

  run_vector_test( model, simple_4_test, k_ary, n_fly )

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness( Component ):

  def construct( s, MsgType, num_routers, src_msgs, sink_msgs,
                 src_initial, src_interval, sink_initial, sink_interval,
                 arrival_time=None ):

    r_rows = k_ary ** ( n_fly - 1 )
    BfPos  = mk_bf_pos( r_rows, n_fly )
    s.dut  = BflyNetworkRTL( MsgType, BfPos, num_routers, 0)

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
# Test cases (specific for 4x4 butterfly)
#-------------------------------------------------------------------------

def test_srcsink_bf4x4():

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
  arrival_pipes = [[3], [5], [7], [9],
                   [9], [7], [5], [3],
                   [3], [5], [7], [9],
                   [9], [7], [5], [3]]
  num_routers = 16
  
  for (src, dst, payload) in test_msgs:
    pkt = mk_bf_pkt( src, dst, 4, 4, 1, payload )
    src_packets [src].append( pkt )
    sink_packets[dst].append( pkt )

  th = TestHarness( BfPacket, num_routers, src_packets, sink_packets, 
                    0, 0, 0, 0, arrival_pipes )

  num_inports = 3 
  for r in range ( num_routers ):
    for i in range (num_inports):
      path_ru_nr = "top.dut.routers[" + str(r) + "].route_units[" + str(i) + "].elaborate.num_routers"
      path_qt      = "top.dut.routers[" + str(r) + "].input_units[" + str(i) + "].elaborate.QueueType"
      th.set_parameter(path_qt,    NormalQueueRTL)
      th.set_parameter(path_ru_nr, num_routers )


#  run_sim( th )

