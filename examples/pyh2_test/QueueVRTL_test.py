"""
==========================================================================
QueueVRTL_test.py
==========================================================================
Imported Queue from SystemVerilog.

Author : Yanghui Ou
  Date : July 10, 2019
"""
from __future__ import absolute_import, division, print_function

import hypothesis
from hypothesis import strategies as st

from pymtl3 import *
from pymtl3.passes import GenDAGPass, OpenLoopCLPass as AutoTickSimPass
from pymtl3.passes.sverilog import ImportPass
from pymtl3.stdlib.test.pyh2.stateful import run_pyh2
from pymtl3.stdlib.test.pyh2.RTL2CLWrapper import RTL2CLWrapper

from .QueueVRTL import Queue, QueueVRTL
from .QueueFL import QueueFL
from .utils import print_header


#-------------------------------------------------------------------------
# Ad-hoc test
#-------------------------------------------------------------------------

def test_adhoc():
  dut = QueueVRTL( Bits16, num_entries=2 )
  dut.elaborate()
  dut = ImportPass()( dut )
  dut.apply( SimulationPass )
  dut.sim_reset()

  # Tick until ready to enq
  while not dut.enq.rdy:
    dut.tick()

  # Enq a message
  dut.enq.en  = b1(1)
  dut.enq.msg = b16(0xface)
  dut.tick()

  # Tick until ready to deq
  dut.enq.en = b1(0)
  while not dut.deq.rdy:
    dut.tick()

  # Deq a message
  dut.deq.en = b1(1)
  assert dut.deq.msg == 0xface

#-------------------------------------------------------------------------
# Openloop test
#-------------------------------------------------------------------------

def test_auto_tick():
  print()
  dut = RTL2CLWrapper(
    QueueVRTL( Bits16, num_entries=2 ),
    { 'enq': Bits16, 'deq': Bits16 },
  )
  dut.elaborate()
  dut = ImportPass()( dut )
  dut.apply( GenDAGPass() )
  dut.apply( AutoTickSimPass() )
  dut.lock_in_simulation()
  dut.sim_reset()

  assert dut.enq.rdy()
  dut.enq( b16(0xbabe) )
  assert dut.enq.rdy()
  dut.enq( b16(0xface) )

  assert dut.deq.rdy()
  assert dut.deq() == 0xbabe
  assert dut.deq.rdy()
  assert dut.deq() == 0xface

#-------------------------------------------------------------------------
# PyH2 test
#-------------------------------------------------------------------------

@hypothesis.settings( deadline=None )
@hypothesis.given( num_entries = st.integers(1, 16) )
def ttest_pyh2( num_entries ):
  print_header( "num_entries = {}".format( num_entries ) )
  run_pyh2( QueueVRTL( Bits16, num_entries ), QueueFL( num_entries ) )
