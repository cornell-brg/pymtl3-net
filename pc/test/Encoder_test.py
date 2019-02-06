from pymtl       import *
from pclib.test  import TestVectorSimulator
from pc.Encoder import Encoder 

def run_test( model, test_vectors ):
  
  model.elaborate()

  def tv_in( model, test_vector ):
    model.in_.value = test_vector[0]

  def tv_out( model, test_vector ):
    assert model.out.value == test_vector[1]

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

def test_encoder_5_directed( dump_vcd, test_verilog ):
  model = Encoder( 5, 3 )
  model.vcd_file = dump_vcd
  if test_verilog:
    model = TranslationTool( model )

  run_test( model, [
    # in          out 
    [ 0b00000, 0  ],
    [ 0b00001, 0  ],
    [ 0b00010, 1  ],
    [ 0b00100, 2  ],
    [ 0b01100, 3  ],
    [ 0b10000, 4  ]
  ] )
