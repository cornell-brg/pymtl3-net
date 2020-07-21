'''
==========================================================================
connects_test.py
==========================================================================
unit tests for connect utils.

Author : Yanghui Ou
  Date : Feb 7, 2020
'''
from pymtl3 import *
from .connects import bitstruct_to_slices, connect_bitstruct

#-------------------------------------------------------------------------
# Bitstructs for unit tests
#-------------------------------------------------------------------------

@bitstruct
class Point:
  x : Bits8
  y : Bits4

@bitstruct
class Nested:
  z    : Bits6
  pt   : Point
  flag : Bits1

#-------------------------------------------------------------------------
# Components for unit tests
#-------------------------------------------------------------------------

class Bits2Bitstruct( Component ):
  def construct( s ):
    s.pt_bits      = InPort ( Bits12 )
    s.pt_bitstruct = OutPort( Point  )
    connect_bitstruct( s.pt_bits, s.pt_bitstruct )

class Bitstruct2Bits( Component ):
  def construct( s ):
    s.pt_bitstruct = InPort ( Point  )
    s.pt_bits      = OutPort( Bits12 )
    connect_bitstruct( s.pt_bitstruct, s.pt_bits )

class Bits2BitstructNested( Component ):
  def construct( s ):
    s.pt_bits      = InPort ( Bits19 )
    s.pt_bitstruct = OutPort( Nested )
    connect_bitstruct( s.pt_bits, s.pt_bitstruct )

class Bitstruct2BitsNested( Component ):
  def construct( s ):
    s.pt_bitstruct = InPort ( Nested )
    s.pt_bits      = OutPort( Bits19 )
    connect_bitstruct( s.pt_bitstruct, s.pt_bits )

#-------------------------------------------------------------------------
# Unit test fos helper funcion
#-------------------------------------------------------------------------

def test_bitstruct_to_slices():
  slices = bitstruct_to_slices( Point )
  assert slices[0] == slice(0, 4 )
  assert slices[1] == slice(4, 12)

  slices_nested = bitstruct_to_slices( Nested )
  assert slices_nested[0] == slice(0,  1 )
  assert slices_nested[1] == slice(1,  5 )
  assert slices_nested[2] == slice(5,  13)
  assert slices_nested[3] == slice(13, 19)

#-------------------------------------------------------------------------
# Unit test fos connect_bitstruct
#-------------------------------------------------------------------------

def test_connect_bitstruct_simple():
  a = Bits2Bitstruct()
  a.elaborate()
  a.apply( DefaultPassGroup() )
  a.pt_bits @= 0xeda
  a.sim_eval_combinational()
  assert a.pt_bitstruct.x == 0xed
  assert a.pt_bitstruct.y == 0xa

  b = Bitstruct2Bits()
  b.elaborate()
  b.apply( DefaultPassGroup() )
  b.pt_bitstruct.x @= 0xed
  b.pt_bitstruct.y @= 0xa
  b.sim_eval_combinational()
  assert b.pt_bits == 0xeda

def test_connect_bitstruct_nested():
  a = Bits2BitstructNested()
  a.elaborate()
  a.apply( DefaultPassGroup() )
  a.pt_bits @= concat( b6(0x3f), b12(0xeda), b1(1) )
  a.sim_eval_combinational()
  assert a.pt_bitstruct.z    == 0x3f
  assert a.pt_bitstruct.pt.x == 0xed
  assert a.pt_bitstruct.pt.y == 0xa
  assert a.pt_bitstruct.flag == 1

  b = Bitstruct2BitsNested()
  b.elaborate()
  b.apply( DefaultPassGroup() )
  b.pt_bitstruct.z    @= 0x3f
  b.pt_bitstruct.pt.x @= 0xed
  b.pt_bitstruct.pt.y @= 0xa
  b.pt_bitstruct.flag @= 0x1
  b.sim_eval_combinational()
  assert b.pt_bits == concat( b6(0x3f), b12(0xeda), b1(1) )

