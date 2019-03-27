#=========================================================================
# SwitchUnitRTL_test.py
#=========================================================================
# Test for SwitchUnitRTL
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 1, 2019

import tempfile
from pymtl                   import *
from pclib.test              import TestVectorSimulator
from ocn_pclib.ifcs.Packet   import Packet, mk_pkt
from router.SwitchUnitRTL    import SwitchUnitRTL

#-------------------------------------------------------------------------
# Test for switch unit with get/send interface 
#-------------------------------------------------------------------------

def run_test_get_send( model, test_vectors ):

  def tv_in( model, test_vector ):

    for i in range( model.num_inports ):
      model.get[i].rdy = test_vector[0][i]
      pkt = mk_pkt( 0, 0, 1, 1, i, test_vector[1][i])
      model.get[i].msg = pkt

    model.send.rdy = test_vector[3]

  def tv_out( model, test_vector ):
    for i in range( model.num_inports ):
      assert model.get[i].en == test_vector[2][i]

    assert model.send.en == test_vector[4]
    if model.send.en == 1:
      assert model.send.msg.payload == test_vector[5]
  
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

def test_get_send( dump_vcd, test_verilog ):

  model = SwitchUnitRTL( Packet )
  x = 'x'
  run_test_get_send( model, [
   #  get.rdy     get.msg       get.en     send.rdy send.en send.msg
   [ [1,0,0,0,0], [5,6,7,8,9],  [0,0,0,0,0],     0,       0,     x    ],
   [ [1,0,0,0,0], [6,7,8,9,5],  [1,0,0,0,0],     1,       1,     6    ],
   [ [1,1,0,0,0], [0,1,2,3,4],  [0,1,0,0,0],     1,       1,     1    ],
   [ [0,1,0,0,0], [1,2,3,4,5],  [0,1,0,0,0],     1,       1,     2    ],
   [ [0,1,1,1,0], [9,8,7,6,5],  [0,0,1,0,0],     1,       1,     7    ],
   [ [0,1,1,1,0], [8,7,6,5,4],  [0,0,0,1,0],     1,       1,     5    ],
   [ [0,1,1,1,0], [7,6,5,4,3],  [0,0,0,0,0],     0,       0,     x    ],
   [ [0,1,1,1,0], [8,7,6,5,4],  [0,1,0,0,0],     1,       1,     7    ],
   [ [0,1,1,1,0], [9,8,7,6,5],  [0,0,1,0,0],     1,       1,     7    ],
   [ [1,1,1,1,1], [5,4,3,2,1],  [0,0,0,1,0],     1,       1,     2    ],
   [ [1,1,1,1,1], [5,4,3,2,1],  [0,0,0,0,1],     1,       1,     1    ],
   [ [1,1,1,1,1], [5,4,3,2,1],  [1,0,0,0,0],     1,       1,     5    ],
  ])
