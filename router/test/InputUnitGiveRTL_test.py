#=========================================================================
# Tests for InputUnitGiveRTL 
#=========================================================================
#
# Author: Yanghui Ou
#   Date: Mar 24, 2019

import pytest

from pymtl                    import *
from pymtl.dsl.test.sim_utils import simple_sim_pass
from pclib.test.test_srcs     import TestSrcRTL
from pclib.test.test_sinks    import TestSinkRTL
from pclib.test               import TestVectorSimulator
from router.InputUnitGiveRTL  import InputUnitGiveRTL 

#-------------------------------------------------------------------------
# TestVectorSimulator test
#-------------------------------------------------------------------------

def run_tv_test( dut, test_vectors ):

  # Define input/output functions

  def tv_in( dut, tv ):
    dut.recv.en  = tv[0]
    dut.recv.msg = tv[2]
    dut.send.en  = tv[3]

  def tv_out( dut, tv ):
    if tv[1] != '?': assert dut.recv.rdy == tv[1]
    if tv[4] != '?': assert dut.send.rdy == tv[4]
    if tv[5] != '?': assert dut.send.msg == tv[5]

  # Run the test

  sim = TestVectorSimulator( dut, test_vectors, tv_in, tv_out )
  sim.run_test()

def test_pipe_Bits():

  B1  = mk_bits(1)
  B32 = mk_bits(32)
  run_tv_test( InputUnitGiveRTL( Bits32 ), [
    #  enq.en  enq.rdy enq.msg   deq.en  deq.rdy deq.msg
    [  B1(1),  B1(1),  B32(123), B1(0),  B1(0),    '?'    ],
    [  B1(1),  B1(1),  B32(345), B1(0),  B1(1),  B32(123) ],
    [  B1(0),  B1(0),  B32(567), B1(0),  B1(1),  B32(123) ],
    [  B1(0),  B1(0),  B32(567), B1(1),  B1(1),  B32(123) ],
    [  B1(0),  B1(1),  B32(567), B1(1),  B1(1),  B32(345) ],
    [  B1(1),  B1(1),  B32(567), B1(0),  B1(0),    '?'    ],
    [  B1(1),  B1(1),  B32(0  ), B1(1),  B1(1),  B32(567) ],
    [  B1(1),  B1(1),  B32(1  ), B1(1),  B1(1),  B32(0  ) ],
    [  B1(1),  B1(1),  B32(2  ), B1(1),  B1(1),  B32(1  ) ],
    [  B1(0),  B1(1),  B32(2  ), B1(1),  B1(1),  B32(2  ) ],
] )
