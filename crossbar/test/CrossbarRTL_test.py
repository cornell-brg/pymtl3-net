#=========================================================================
# CrossbarRTL_test.py
#=========================================================================
# Test for CrossbarRTL
#
# Author : Cheng Tan, Yanghui Ou
#   Date : April 18, 2019

import tempfile
from pymtl                   import *
from crossbar.CrossbarRTL    import CrossbarRTL
from ocn_pclib.rtl.queues    import NormalQueueRTL
from pclib.test.test_srcs    import TestSrcRTL
from pclib.test.test_sinks   import TestSinkRTL
from pclib.test              import TestVectorSimulator
from ocn_pclib.ifcs.Packet   import * 
from ocn_pclib.ifcs.Position import *
from ocn_pclib.ifcs.Flit     import *

#-------------------------------------------------------------------------
# Test Vector
#-------------------------------------------------------------------------

def run_vector_test( model, test_vectors, num_terminals ):
 
  def tv_in( model, test_vector ):

    if test_vector[0] != 'x':
      ter_id = test_vector[0]
#      pkt = mk_pkt( router_id, 0, test_vector[1][0], 0, 1, test_vector[1][1])
      pkt = mk_base_pkt( ter_id, test_vector[1][0], 1, test_vector[1][1])
      flits = flitisize_ring_flit( pkt, 1, num_terminals )

      # Enable the network interface on specific router
      for i in range (num_terminals):
        model.recv[i].en  = 0
      model.recv[ter_id].msg = flits[0]
      model.recv[ter_id].en  = 1

    for i in range (num_terminals):
      model.send[i].rdy = 1

  def tv_out( model, test_vector ):
    if test_vector[2] != 'x':
      pkt = model.send[test_vector[2]].msg.payload
      assert pkt.payload == test_vector[3]
     
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()
  model.sim_reset()

def test_vector_crossbar2( dump_vcd, test_verilog ):

  num_terminals  = 2
  RingFlit = mk_ring_flit( 1, num_terminals )
  model = CrossbarRTL( RingFlit, num_terminals )

  num_inports = 3
  model.set_parameter( "top.input_units*.elaborate.QueueType", NormalQueueRTL )

  x = 'x'

  # Specific for wire connection (link delay = 0) in 2x2 Torus topology
  simple_2_test = [
#  termi   [packet]   arr_ter  msg 
  [  0,    [0,1001],     x,       x  ],
  [  0,    [1,1002],     0,     1001 ],
  [  0,    [1,1003],     1,     1002  ],
  [  0,    [1,1004],     1,     1003 ],
  [  0,    [0,1005],     1,     1004 ],
  [  x,    [0,0000],     0,     1005 ],
  [  x,    [0,0000],     x,       x  ],
  [  x,    [0,0000],     x,       x  ],
  [  x,    [0,0000],     x,       x  ],
  [  x,    [0,0000],     x,       x  ],
  [  x,    [0,0000],     x,       x  ],
  [  x,    [0,0000],     x,       x  ],
  [  x,    [0,0000],     x,       x  ],
  ]

  run_vector_test( model, simple_2_test, num_terminals)


