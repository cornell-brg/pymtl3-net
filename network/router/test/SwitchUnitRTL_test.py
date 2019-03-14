#=========================================================================
# SwitchUnitRTL_test.py
#=========================================================================
# Test for SwitchUnitRTL
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 1, 2019

import tempfile
from pymtl                import *
from ocn_pclib.TestVectorSimulator            import TestVectorSimulator
from network.router.SwitchUnitRTL import SwitchUnitRTL

def run_test( model, test_vectors ):
 
#  model.elaborate()

  def tv_in( model, test_vector ):
    model.send.rdy = test_vector[2]
#    model.send.en  = test_vector[3]
    for i in range( model.num_inports ):
      model.recv[i].en = test_vector[0][i]
      model.recv[i].msg = test_vector[1][i]

  def tv_out( model, test_vector ):
    assert Bits16(model.send.en)  == Bits16(test_vector[3])
    assert Bits16(model.send.msg) == Bits16(test_vector[4])
  
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

def test_SwitchUnit( dump_vcd, test_verilog ):
  model = SwitchUnitRTL(Bits16)

  run_test( model, [
    # recv_en        msg     send_rdy   send_en     send_msg 
   [[1,0,0,0,0], [5,6,7,8,9],    0,         0,          5    ],
   [[0,0,0,0,0], [5,6,7,8,9],    1,         1,          5    ],
   [[0,1,0,0,0], [1,2,3,4,5],    1,         1,          2    ],
   [[0,1,1,1,0], [9,8,7,6,5],    0,         0,          7    ],
   [[0,1,1,1,0], [8,7,6,5,4],    0,         0,          7    ],
   [[0,1,1,1,0], [9,8,7,6,5],    1,         1,          7    ],
   [[0,1,1,1,0], [8,7,6,5,4],    0,         0,          6    ],
   [[0,1,1,1,0], [9,8,7,6,5],    0,         0,          6    ],
   [[0,1,1,1,0], [5,4,3,2,1],    1,         1,          6    ],
   [[1,0,0,0,1], [3,4,5,6,7],    1,         1,          7    ],
   [[0,1,1,0,1], [3,4,5,6,7],    1,         1,          3    ],
  ])
