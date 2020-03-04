'''
==========================================================================
PitonNoCHeader.py
==========================================================================
Bitstruct definition for open-piton network header.

Author : Yanghui Ou
  Date : Mar 4, 2020
'''
from pymtl3 import *

@bistruct
class PitonNoCHeader:
  chipid : Bits14
  xpos   : Bits8
  ypos   : Bits8
  fbits  : Bits4
  plen   : Bits8
  mtype  : Bits8
  mshr   : Bits8
  opt1   : Bits6

  def __str__( s ):
    return f'{s.chipid[13]:({s.xpos},{s.ypos}):{s.plen}}'

