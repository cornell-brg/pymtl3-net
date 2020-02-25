'''
==========================================================================
commons_test.py
==========================================================================
Unit tests for common utilities.

Author : Yanghui Ou
  Date : Feb 10, 2020
'''
from pymtl3 import *
from .commons import get_nbits, to_bits, to_bitstruct

#-------------------------------------------------------------------------
# Bitstruct for unit tests
#-------------------------------------------------------------------------

@bitstruct
class Point:
  x : Bits4
  y : Bits8

@bitstruct
class PointAlt:
  x : Bits8
  y : Bits4

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

#-------------------------------------------------------------------------
# test_to_bits
#-------------------------------------------------------------------------

def test_to_bits():
  pt = Point( 0xe, 0xdc )
  nested = Nested( pt, z=0xba )
  assert to_bits( pt ) == 0xedc
  assert to_bits( nested ) == 0xedcba

#-------------------------------------------------------------------------
# test_to_bitstruct
#-------------------------------------------------------------------------

def test_to_bitstruct():
  bits = b12( 0xcba )
  pt1 = to_bitstruct( bits, Point    )
  assert pt1.x == 0xc
  assert pt1.y == 0xba

  pt2 = to_bitstruct( bits, PointAlt )
  assert pt2.x == 0xcb
  assert pt2.y == 0xa

  pt3 = to_bitstruct( pt1, PointAlt )
  assert pt3.x == 0xcb
  assert pt3.y == 0xa

  pt4 = to_bitstruct( pt2, Point    )
  assert pt4.x == 0xc
  assert pt4.y == 0xba

