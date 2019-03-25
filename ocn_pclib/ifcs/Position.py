#=========================================================================
# Position.py
#=========================================================================
# Position formats for different network topologies
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 6, 2019

from pymtl import *

#-------------------------------------------------------------------------
# MeshPosition
#-------------------------------------------------------------------------

class MeshPosition( object ): 
  
  def __init__( s, mesh_wid=2, mesh_ht=2 ):
    
    XType = mk_bits( clog2( mesh_wid ) )
    YType = mk_bits( clog2( mesh_ht  ) )

    s.pos_x  = XType( 0 )
    s.pos_y  = YType( 0 ) 

  def __str__( s ):
    return "({},{})".format( s.pos_x, s.pos_y )

#-------------------------------------------------------------------------
# RingPosition
#-------------------------------------------------------------------------

class RingPosition( object ):

  def __init__( s, num_nodes=2 ):
    
    Type = mk_bits( clog2( num_nodes ) )

    s.pos = Type( 0 )

  def __str__( s ):
    return "{}".format( s.pos )

#-------------------------------------------------------------------------
# Utility functions
#-------------------------------------------------------------------------

def mk_mesh_pos( pos_x=0, pos_y=0, mesh_wid=2, mesh_ht=2 ):

  pos = MeshPosition( mesh_wid, mesh_ht )
  pos.pos_x = pos_x
  pos.pos_y = pos_y

  return pos

def mk_mesh_pos_list( mesh_wid=2, mesh_ht=2 ):

  pos_list = []

  for c in range( mesh_wid ):
    for r in range( mesh_ht ):
      pos_list.append( mk_mesh_pos( c, r, mesh_wid, mesh_ht ) ) 

  return pos_list

