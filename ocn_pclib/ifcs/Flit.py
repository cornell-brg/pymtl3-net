#=========================================================================
# Flit.py
#=========================================================================
# Flit format for OCN generator
#
# Author : Cheng Tan
#   Date : Mar 30, 2019

from pymtl import *

import py

#-------------------------------------------------------------------------
# Static Flit type
#-------------------------------------------------------------------------

class Flit( object ):

  def __init__( s ):
    
    s.id    = Bits4 ( 0 )
    s.src   = Bits4 ( 0 )
    s.dst   = Bits4 ( 0 ) 
    s.type  = Bits4 ( 0 )
    s.opaque  = Bits4 ( 0 ) 
    s.payload = Bits16( 0 )

  def __str__( s ):
    return "{}:({})>({}):{}:{}:{}".format(
      s.id, s.src, s.dst, s.type, s.opaque, s.payload ) 

def mk_flit( id, src, dst, opaque=1, payload=0, size=4 ):
  flit = Flit()
  flit.id      = id
  flit.src     = src
  flit.dst     = dst
  flit.opaque  = opaque
  flit.payload = payload
  
  HEAD = 0
  BODY = 1
  TAIL = 2

  if id == 0:
    flit.type = HEAD;
  elif id == size - 1:
    flit.type = TAIL;
  else:
    flit.type = BODY;

  return flit

