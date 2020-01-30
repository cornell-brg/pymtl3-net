'''
==========================================================================
packet_format_test.py
==========================================================================
Unit tests for packet_format decorator.

Author : Yanghui Ou
  Date : Jan 29, 2020
'''
from .packet_formats import packet_format

@packet_format( 24 )
class MyFormat:
  # Field  LO  HI
  OPAQUE : ( 16, 24 )
  XPOS   : ( 8,  16 )
  YPOS   : ( 0,  8  )

def test_simple_format():
  assert MyFormat.OPAQUE == slice(16, 24)
  assert MyFormat.XPOS   == slice(8,  16)
  assert MyFormat.YPOS   == slice(0,  8 )
  print( MyFormat.__dict__ )
