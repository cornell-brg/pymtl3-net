'''
==========================================================================
commons_test.py
==========================================================================
Unit tests for common utilities.

Author : Yanghui Ou
  Date : Feb 10, 2020
'''
from pymtl3 import *
from .commons import get_nbits

#-------------------------------------------------------------------------
# Bitstruct for unit tests
#-------------------------------------------------------------------------

@bitstruct
class Point:
  x : Bits4
  y : Bits8

@bitstruct
class Nested:
  pt : Point
  z  : Bits8

#-------------------------------------------------------------------------
# test_get_nbits
#-------------------------------------------------------------------------

def test_get_nbits():
  assert get_nbits( Point  ) == 12
  assert get_nbits( Nested ) == 20

