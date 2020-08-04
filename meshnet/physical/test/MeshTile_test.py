'''
==========================================================================
MeshTile_test.py
==========================================================================
Some simple tests for the MeshTile.

Author : Yanghui Ou
  Date : July 30, 2020
'''
from pymtl3 import *
from pymtl3.passes.backends.verilog import *
from ocnlib.rtl.queues import NormalQueueRTL as Queue

from ..MeshTile import MeshTile

@bitstruct
class Header64:
  src_x : Bits8
  src_y : Bits8
  dst_x : Bits8
  dst_y : Bits8
  plen  : Bits4
  filler: Bits28

@bitstruct
class Position:
  pos_x : Bits8
  pos_y : Bits8

def test_translate():
  assert Header64.nbits == 64
  assert Position.nbits == 16

  dut = MeshTile( Header64, Position )
  dut.set_param( 'top.router.input_units*.construct', QueueType=Queue )
  dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'MeshTile' )
  dut.set_metadata( VerilogTranslationImportPass.enable, True )
  dut.elaborate()
  dut = VerilogTranslationImportPass()( dut )

  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()

