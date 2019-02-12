import tempfile
from pymtl                import *
from pclib.test           import TestVectorSimulator, TestSource, TestSink
from router.SwitchUnit import SwitchUnit

def run_test( model, test_vectors ):
 
  model.elaborate()

  def tv_in( model, test_vector ):
    model.out.rdy.value = test_vector[2]
    for i in range( model.num_inports ):
      if i == test_vector[0]:
        model.in_[i].val.value = 1
        model.in_[i].msg.value = test_vector[1]
      else:
        model.in_[i].val.value = 0
        model.in_[i].msg.value = 0

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
    # val_index   msg      out_rdy    out_val    out_msg 
   [     1,        7,         0,         1,         '?'   ],
   [     4,        9,         0,         1,          9    ],
   [     2,        5,         0,         1,          5    ],
   [     3,        2,         1,         1,          2    ],
   [     0,        4,         1,         1,          4    ],
  ])

#  run_test( model, [
#    # reqs    hold grants      priority
#    [ 0b0000, 0,   0b0000 ], # 0001
#    [ 0b1000, 0,   0b1000 ], # 0001
#    [ 0b1100, 0,   0b0100 ], # 0100  
#    [ 0b1100, 0,   0b1000 ], # 1000
#    [ 0b0000, 1,   0b1000 ], # 1000
#    [ 0b0111, 0,   0b0001 ], # 1000
#    [ 0b1111, 0,   0b0010 ], # 0010
#    [ 0b1111, 1,   0b0010 ], # 0010
#    [ 0b1111, 1,   0b0010 ], # 0010
#  ] )

