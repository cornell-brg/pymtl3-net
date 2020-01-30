'''
==========================================================================
SwitchUnitMFlitRTL_test.py
==========================================================================

Author : Yanghui Ou
  Date : Jan 28, 2020
'''
from pymtl3 import *
from pymtl3.passes.backends.yosys import TranslationImportPass
from ocnlib.packets import packet_format
from ..SwitchUnitMFlitRTL import SwitchUnitMFlitRTL

def test_sanity_check():

  @packet_format( 8 )
  class DummyFormat:
    PLEN : ( 0, 8 )

  dut = SwitchUnitMFlitRTL( DummyFormat, num_inports=5 )
  dut.elaborate()
  print( dut.mux_out_PLEN )
  dut.yosys_translate_import = True
  dut = TranslationImportPass()( dut )
  dut.elaborate()

  dut.apply( SimulationPass() )
  dut.sim_reset()
  dut.tick()
