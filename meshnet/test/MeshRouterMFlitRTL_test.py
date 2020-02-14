'''
==========================================================================
MeshRouterMFlitRTL_test.py
==========================================================================
Test cases for mesh router that supports multi-flit packet.

Author : Yanghui Ou
  Date : Feb 13, 2020
'''
import pytest
from pymtl3 import *
from pymtl3.stdlib.test import mk_test_case_table
from ocnlib.utils import to_bitstruct
from ocnlib.packets import MultiFlitPacket as Packet

from ..MeshRouterFL import MeshRouterMFlitFL
from ..MeshRouterMFlitRTL import MeshRouterMFlitRTL

#-------------------------------------------------------------------------
# helper stuff
#-------------------------------------------------------------------------

@bitstruct
class TestHeader:
  opaque : Bits12
  src_x  : Bits4
  src_y  : Bits4
  dst_x  : Bits4
  dst_y  : Bits4
  plen   : Bits4

@bitstruct
class TestPosition:
  pos_x : Bits4
  pos_y : Bits4

#-------------------------------------------------------------------------
# run_sim
#-------------------------------------------------------------------------
# TODO: use stdlib run_sim omce pymtl3 is updated

def run_sim( th, max_cycles=200 ):
  th.elaborate()
  th.apply( SimulationPass() )
  th.sim_reset()

  ncycles = 0
  while not th.done() and ncycles < max_cycles:
    print( f'{ncycles:3}:{th.line_trace()}' )
    th.tick()
    ncycles += 1

  assert th.done()
  th.tick()
  th.tick()
  th.tick()

#-------------------------------------------------------------------------
# mk_pkt
#-------------------------------------------------------------------------

def mk_pkt( dst_x, dst_y, payload=[], src_x=0, src_y=0, opaque=0 ):
  plen        = len( payload )
  header      = TestHeader( opaque, plen, src_x, src_y, dst_x, dst_y )
  header_bits = to_bits( header )
  flits       = [ header_bits ] + payload
  return Packet( TestHeader, flits )

#-------------------------------------------------------------------------
# sanity check
#-------------------------------------------------------------------------

def test_sanity_check():
  dut = MeshRouterMFlitRTL( TestHeader, TestPosition )
  dut.elaborate()
  dut.apply( SimulationPass() )
  dut.sim_reset()
  dut.tick()