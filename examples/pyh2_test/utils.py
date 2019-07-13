"""
==========================================================================
utils.py
==========================================================================
Utilities for PyH2 test.

Author : Yanghui Ou
  Date : July 12, 2019
"""
from __future__ import absolute_import, division, print_function

try:
  from termcolor import colored
  colored_installed = True
except:
  colored_installed = False

#-------------------------------------------------------------------------
# print_header
#-------------------------------------------------------------------------

if colored_installed:
  def print_header( text, header_len=78, color='green' ):
    print( colored('='*header_len, color) )
    print( colored(text, color) )
    print( colored('='*header_len, color) )
else:
  def print_header( text, header_len=78, color='green' ):
    print( '='*header_len )
    print( text )
    print( '='*header_len )