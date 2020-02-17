'''
==========================================================================
BoundaryUnit.py
==========================================================================
Error check unit that solves the dangling caller port issue.

Author : Yanghui Ou
  Date : Feb 17, 2020
'''
from pymtl3 import *

class BoundaryUnit( Component ):

  def construct( s, default_rdy=False ):
    s.default_rdy = default_rdy

  @non_blocking( lambda s: s.default_rdy )
  def recv( s, *args, **kwargs ):
    assert False, f'Boundary unit {s} is not supposed to receive any message!'
