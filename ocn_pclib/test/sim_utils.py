from pymtl3 import *
from pymtl3.passes.backends.sverilog import TranslationImportPass as SVTransImport
from pymtl3.passes.backends.sverilog import ImportConfigs as SVConfig 
from pymtl3.passes.backends.yosys import TranslationImportPass as YSTransImport
from pymtl3.passes.backends.yosys import ImportConfigs as YSConfig

# Assumes th.dut
def run_sim( th, max_cycles=1000, translation='', trace=True, verilator_vcd=False ):

  th.elaborate()

  if translation == 'sverilog':
    TransImport = SVTransImport
    th.dut.sverilog_translate_import = True
    if verilator_vcd:
      th.dut.config_sverilog_import = SVConfig(
        vl_trace = True,
      )

  elif translation == 'yosys':
    TransImport = YSTransImport
    th.dut.yosys_translate_import = True
    if verilator_vcd:
      th.dut.config_yosys_import = YSConfig(
        vl_trace = True,
      )

  if translation:
    th = TransImport()( th )
    th.elaborate()

  th.apply( SimulationPass() )
  th.sim_reset()

  # Run simulation
  ncycles = 0

  if trace:
    print()
    print( "{:3}:{}".format( ncycles, th.line_trace() ))

  while not th.done() and ncycles <= max_cycles:
    th.tick()
    ncycles += 1
    if trace: print( "{:3}:{}".format( ncycles, th.line_trace() ))

  # Check timeout
  # assert ncycles < max_cycles
  if ncycles > max_cycles:
    raise Exception( f'Timeout: simulation did not finish in {max_cycles} cycles!' )
