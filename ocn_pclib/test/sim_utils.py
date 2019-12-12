from pymtl3 import *


def run_sim( th, max_cycles=1000 ):
  th.apply( SimulationPass() )
  th.sim_reset()

  # Run simulation
  ncycles = 0
  print()
  print( "{:3}:{}".format( ncycles, th.line_trace() ))
  while not th.done() and ncycles < max_cycles:
    th.tick()
    ncycles += 1
    print( "{:3}:{}".format( ncycles, th.line_trace() ))

  # Check timeout
  assert ncycles < max_cycles
