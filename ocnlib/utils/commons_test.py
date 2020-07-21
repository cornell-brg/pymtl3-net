'''
==========================================================================
commons_test.py
==========================================================================
Unit tests for common utilities.

Author : Yanghui Ou
  Date : Feb 10, 2020
'''
from pymtl3 import *

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
# test_nbits
#-------------------------------------------------------------------------

def test_nbits():
  assert Point.nbits == 12
  assert Nested.nbits == 20

#-------------------------------------------------------------------------
# test_to_bits
#-------------------------------------------------------------------------

def test_to_bits():
  pt = Point( 0xe, 0xdc )
  nested = Nested( pt, z=0xba )
  assert pt.to_bits() == 0xedc
  assert nested.to_bits() == 0xedcba

#-------------------------------------------------------------------------
# test_to_bitstruct
#-------------------------------------------------------------------------

def test_to_bitstruct():
  bits = b12( 0xcba )
  pt1 = Point.from_bits( bits )
  assert pt1.x == 0xc
  assert pt1.y == 0xba

  pt2 = PointAlt.from_bits( bits )
  assert pt2.x == 0xcb
  assert pt2.y == 0xa

  pt3 = PointAlt.from_bits( pt1 )
  assert pt3.x == 0xcb
  assert pt3.y == 0xa

  pt4 = Point.from_bits( pt2 )
  assert pt4.x == 0xc
  assert pt4.y == 0xba

