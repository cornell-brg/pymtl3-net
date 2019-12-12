"""
==========================================================================
pymtl3-net-test.py
==========================================================================
A regression test to test out all possible commands of pymtl3-net script.

Author: Shunning Jiang
  Date: Dec 11, 2019

"""
import os
from subprocess import check_output, CalledProcessError

nets = ['ring', 'torus', 'mesh', 'cmesh', 'bfly']

sim_dir = os.path.dirname( os.path.abspath( __file__ ) )
sim     = sim_dir + os.path.sep + 'pymtl3-net'

def command( cmd ):
  print(" ".join(cmd))
  try:
    result = check_output( cmd ).strip()
  except CalledProcessError as e:
    raise Exception( "Error running simulator!\n\n"
                     "Simulator command line: {cmd}\n\n"
                     "Simulator output:\n {output}"
                     .format( cmd=' '.join(e.cmd), output=e.output ) )

def test_gen():
  for net in nets:
    filename = f"{net}.sv"
    if os.path.exists( filename ):
      os.remove( filename )
    command( [ sim, 'gen', net ] )
    assert os.path.exists( filename )

def test_test():
  for net in nets:
    command( [ sim, 'test', net ] )
