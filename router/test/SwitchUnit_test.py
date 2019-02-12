import tempfile
from pymtl                import *
from pclib.test           import TestVectorSimulator, TestSource, TestSink
from router.SwitchUnit import SwitchUnit

def run_test( model, test_vectors ):
 
  model.elaborate()

  def tv_in( model, test_vector ):
    model.out.rdy.value = test_vector[2]
    for i in range( model.num_inports ):
      model.in_[i].val.value = test_vector[0][i]
      model.in_[i].msg.value = test_vector[1][i]

  def tv_out( model, test_vector ):
    if test_vector[4] != '?':
      assert model.out.val == test_vector[3]
      if model.out.val == 1:      
        assert model.out.msg == test_vector[4]
  
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

def test_SwitchUnit( dump_vcd, test_verilog ):
  model = SwitchUnit( 16, 5 )

  run_test( model, [
    # val            msg      out_rdy    out_val    out_msg 
   [[0,0,0,0,0], [5,6,7,8,9],    0,         0,         '?'   ],
   [[0,1,0,0,0], [1,2,3,4,5],    1,         1,          2    ],
   [[0,1,1,1,0], [9,8,7,6,5],    1,         1,          7    ],
   [[0,1,1,1,0], [5,4,3,2,1],    1,         1,          2    ],
   [[1,0,0,0,1], [3,4,5,6,7],    1,         1,          7    ],
   [[0,1,1,0,1], [3,4,5,6,7],    1,         1,          4    ],
  ])

#  run_test( model, [
#    # val_index   msg      out_rdy    out_val    out_msg 
#   [     1,        7,         0,         1,         '?'   ],
#   [     4,        9,         0,         1,          9    ],
#   [     2,        5,         0,         1,          5    ],
#   [     3,        2,         1,         1,          2    ],
#   [     0,        4,         1,         1,          4    ],
#  ])












