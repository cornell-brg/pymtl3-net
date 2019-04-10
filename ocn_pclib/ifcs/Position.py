#=========================================================================
# Position.py
#=========================================================================
# Position formats for different network topologies
#
# Author : Yanghui Ou, Cheng Tan
#   Date : Mar 25, 2019

from pymtl import *

import py

#-------------------------------------------------------------------------
# Base MeshPosition
#-------------------------------------------------------------------------

class BaseMeshPosition( object ): 

  def __init__( s, pox_x=0, pos_y=0, mesh_wid=2, mesh_ht=2 ):
    
    XType = mk_bits( clog2( mesh_wid ) )
    YType = mk_bits( clog2( mesh_ht  ) )

    s.pos_x = XType( 0 )
    s.pos_y = YType( 0 ) 

  def __str__( s ):
    return "({},{})".format( s.pos_x, s.pos_y )

#-------------------------------------------------------------------------
# Dynamically generated MeshPosition
#-------------------------------------------------------------------------

_mesh_pos_dict = dict()
# _mesh_pos_template = """
# class MeshPosition_{mesh_wid}_by_{mesh_ht}( object ):
# 
#   def __init__( s, pos_x=0, pos_y=0 ):
# 
#     XType = mk_bits( clog2( {mesh_wid} ) )
#     YType = mk_bits( clog2( {mesh_ht}  ) )
# 
#     s.pos_x = XType( pos_x )
#     s.pos_y = YType( pos_y )
# 
#   def __str__( s ):
#     return "({{}},{{}})".format( s.pos_x, s.pos_y )
# 
# _mesh_pos_dict[ ( {mesh_wid}, {mesh_ht} ) ] = MeshPosition_{mesh_wid}_by_{mesh_ht}
# """
# 
# def mk_mesh_pos( wid, ht ):
#   if ( wid, ht ) in _mesh_pos_dict:
#     return _mesh_pos_dict[ ( wid, ht ) ]
#   else:
#     exec py.code.Source( 
#       _mesh_pos_template.format( mesh_wid=wid, mesh_ht=ht )
#     ).compile() in globals()
#     return _mesh_pos_dict[ ( wid, ht ) ]

def mk_mesh_pos( mesh_wid, mesh_ht ):

  if ( mesh_wid, mesh_ht ) in _mesh_pos_dict:
    return _mesh_pos_dict[ ( mesh_wid, mesh_ht ) ]

  else:
    XType = mk_bits( clog2( mesh_wid ) )
    YType = mk_bits( clog2( mesh_ht  ) )
    cls_name = "MeshPosition_" + str( mesh_wid ) + "_by_" + str( mesh_ht )

    def __init__( s, pos_x=0, pos_y=0 ):
      s.pos_x = XType( pos_x )
      s.pos_y = YType( pos_y )

    new_class = type( cls_name, ( BaseMeshPosition, ), {"__init__":__init__} )
    _mesh_pos_dict[ ( mesh_wid, mesh_ht ) ] = new_class
    return new_class

#-------------------------------------------------------------------------
# Static RingPosition
#-------------------------------------------------------------------------

class RingPosition( object ):

  def __init__( s, num_nodes=2 ):
    
    Type = mk_bits( clog2( num_nodes ) )

    s.pos = Type( 0 )

  def __str__( s ):
    return "{}".format( s.pos )

#-------------------------------------------------------------------------
# Dynamically generated RingPosition
#-------------------------------------------------------------------------

_ring_pos_dict = dict()
_ring_pos_template = """
class RingPosition_{num_nodes}( object ):
  
  def __init__( s, pos=0 ):

    Type = mk_bits( clog2( {num_nodes} ) )

    s.pos = Type( pos )

  def __str__( s ):
    return "{{}}".format( int( s.pos ) )

_ring_pos_dict[ {num_nodes} ] = RingPosition_{num_nodes}
"""

def mk_ring_pos( num_nodes ):
  if (num_nodes) in _ring_pos_dict:
    return _ring_pos_dict[ (num_nodes) ]
  else:
    exec py.code.Source( 
      _ring_pos_template.format( num_nodes = num_nodes ) 
    ).compile() in globals()
    return _ring_pos_dict[ num_nodes ]

#-------------------------------------------------------------------------
# Static ButterflyPosition
#-------------------------------------------------------------------------

class BfPosition( object ):

  def __init__( s, num_nodes=2 ):
    
    Type = mk_bits( clog2( num_nodes ) )

    s.pos = Type( 0 )

  def __str__( s ):
    return "{}".format( s.pos )

#-------------------------------------------------------------------------
# Dynamically generated ButterflyPosition
#-------------------------------------------------------------------------

_bf_pos_dict = dict()
_bf_pos_template = """
class BfPosition_{num_nodes}( object ):
  
  def __init__( s, pos=0 ):

    Type = mk_bits( clog2( {num_nodes} ) )

    s.pos = Type( pos )

  def __str__( s ):
    return "{{}}".format( int( s.pos ) )

_bf_pos_dict[ {num_nodes} ] = BfPosition_{num_nodes}
"""

def mk_bf_pos( num_nodes ):
  if (num_nodes) in _bf_pos_dict:
    return _bf_pos_dict[ (num_nodes) ]
  else:
    exec py.code.Source( 
      _bf_pos_template.format( num_nodes = num_nodes ) 
    ).compile() in globals()
    return _bf_pos_dict[ num_nodes ]


#-------------------------------------------------------------------------
# Utility functions
#-------------------------------------------------------------------------

def mk_mesh_pos_list( mesh_wid=2, mesh_ht=2 ):

  pos_list = []

  for c in range( mesh_wid ):
    for r in range( mesh_ht ):
      pos_list.append( mk_mesh_pos( c, r, mesh_wid, mesh_ht ) ) 

  return pos_list
