'''
==========================================================================
BoundaryUnit_test.py
==========================================================================
Unit test for the boundary unit.

Author : Yanghui Ou
  Date : Feb 17, 2020
'''
from pymtl3 import *
from .BoundaryUnit import BoundaryUnit

def test_false():
  m = BoundaryUnit( default_rdy=False )
  m.elaborate()
  m.apply( SimulationPass() )
  m.tick()
  assert not m.recv.rdy()

  try:
    m.recv( 1 )
    flag = False
  except AssertionError:
    flag = True
  
  assert flag

def test_true():
  m = BoundaryUnit( default_rdy=True )
  m.elaborate()
  m.apply( SimulationPass() )
  m.tick()
  assert m.recv.rdy()

  try:
    m.recv( 1 )
    flag = False
  except AssertionError:
    flag = True
  
  assert flag
