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
class Header32:
  dst_x : Bits8
  dst_y : Bits8
  plen  : Bits4
  filler: Bits12

@bitstruct
class Header64:
  src_x : Bits8
  src_y : Bits8
  dst_x : Bits8
  dst_y : Bits8
  plen  : Bits4
  filler: Bits28

@bitstruct
class Header128:
  src_x : Bits8
  src_y : Bits8
  dst_x : Bits8
  dst_y : Bits8
  plen  : Bits4
  filler: Bits92

@bitstruct
class Header256:
  src_x : Bits8
  src_y : Bits8
  dst_x : Bits8
  dst_y : Bits8
  plen  : Bits4
  filler: Bits220

@bitstruct
class Header512:
  src_x : Bits8
  src_y : Bits8
  dst_x : Bits8
  dst_y : Bits8
  plen  : Bits4
  filler: mk_bits(476)

@bitstruct
class Position:
  pos_x : Bits8
  pos_y : Bits8

@bitstruct
class Position8:
  pos_x : Bits4
  pos_y : Bits4

def test_translate_32b0p():
  nbits                  = 32
  pipe_statge            = 0
  assert Header32.nbits  == nbits
  assert Position.nbits  == 16

  dut = MeshTile( Header32, Position )
  dut.set_param( 'top.router.input_units*.construct', QueueType=Queue )
  dut.set_param( 'top.router.output_units*.construct', QueueType=None, data_gating=False )
  dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'MeshTile_{nbits}b{pipe_statge}p' )
  dut.set_metadata( VerilogTranslationImportPass.enable, True )
  dut.elaborate()
  dut = VerilogTranslationImportPass()( dut )

  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()

def test_translate_32b1p():
  nbits                  = 32
  pipe_statge            = 1
  assert Header32.nbits  == nbits
  assert Position.nbits  == 16

  dut = MeshTile( Header32, Position )
  dut.set_param( 'top.router.input_units*.construct', QueueType=Queue )
  dut.set_param( 'top.router.output_units*.construct', QueueType=Queue, data_gating=False )
  dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'MeshTile_{nbits}b{pipe_statge}p' )
  dut.set_metadata( VerilogTranslationImportPass.enable, True )
  dut.elaborate()
  dut = VerilogTranslationImportPass()( dut )

  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()

def test_translate_64b1p():
  assert Header64.nbits == 64
  assert Position.nbits == 16

  dut = MeshTile( Header64, Position )
  dut.set_param( 'top.router.input_units*.construct', QueueType=Queue )
  dut.set_param( 'top.router.output_units*.construct', QueueType=Queue, data_gating=False )
  dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'MeshTile_64b1p' )
  dut.set_metadata( VerilogTranslationImportPass.enable, True )
  dut.elaborate()
  dut = VerilogTranslationImportPass()( dut )

  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()

def test_translate_128b0p():
  nbits                  = 128
  pipe_statge            = 0
  assert Header128.nbits == nbits
  assert Position.nbits  == 16

  dut = MeshTile( Header128, Position )
  dut.set_param( 'top.router.input_units*.construct', QueueType=Queue )
  dut.set_param( 'top.router.output_units*.construct', QueueType=None, data_gating=False )
  dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'MeshTile_{nbits}b{pipe_statge}p' )
  dut.set_metadata( VerilogTranslationImportPass.enable, True )
  dut.elaborate()
  dut = VerilogTranslationImportPass()( dut )

  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()

def test_translate_128b1p():
  nbits                  = 128
  pipe_statge            = 1
  assert Header128.nbits == nbits
  assert Position.nbits  == 16

  dut = MeshTile( Header128, Position )
  dut.set_param( 'top.router.input_units*.construct', QueueType=Queue )
  dut.set_param( 'top.router.output_units*.construct', QueueType=Queue, data_gating=False )
  dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'MeshTile_{nbits}b{pipe_statge}p' )
  dut.set_metadata( VerilogTranslationImportPass.enable, True )
  dut.elaborate()
  dut = VerilogTranslationImportPass()( dut )

  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()

def test_translate_256b1p():
  nbits                  = 256
  pipe_statge            = 1
  assert Header256.nbits == nbits
  assert Position.nbits  == 16

  dut = MeshTile( Header256, Position )
  dut.set_param( 'top.router.input_units*.construct', QueueType=Queue )
  dut.set_param( 'top.router.output_units*.construct', QueueType=Queue, data_gating=False )
  dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'MeshTile_{nbits}b{pipe_statge}p' )
  dut.set_metadata( VerilogTranslationImportPass.enable, True )
  dut.elaborate()
  dut = VerilogTranslationImportPass()( dut )

  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()

def test_translate_512b1p():
  nbits                  = 512
  pipe_statge            = 1
  assert Header512.nbits == nbits
  assert Position.nbits  == 16

  dut = MeshTile( Header512, Position )
  dut.set_param( 'top.router.input_units*.construct', QueueType=Queue )
  dut.set_param( 'top.router.output_units*.construct', QueueType=Queue, data_gating=False )
  dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'MeshTile_{nbits}b{pipe_statge}p' )
  dut.set_metadata( VerilogTranslationImportPass.enable, True )
  dut.elaborate()
  dut = VerilogTranslationImportPass()( dut )

  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()

