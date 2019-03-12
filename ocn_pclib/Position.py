#=========================================================================
# Position.py
#=========================================================================
# Position formats for different network topologies
#
# Author : Cheng Tan
#   Date : Mar 6, 2019

from pymtl import *

class MeshPosition( object ):
  def __init__(s, pos_id=0, pos_x=0, pos_y=0, size=0):
    
    s.pos_id = pos_id
    s.pos_x  = Bits4 ( pos_x )
    s.pos_y  = Bits4 ( pos_y ) 

  def line_trace( s ):
    return "{} ({},{})".format( s.pos_id, s.pos_x, s.pos_y )

class RingPosition( object ):
  def __init__(s, pos_id=0, size=0):
    
    s.pos_id = pos_id

#def mk_pos( Topology ):
def mk_pos( pos_id=0, pos_x=0, pos_y=0, size=0 ):
  pos = MeshPosition( pos_id, pos_x, pos_y, size )
  return pos

