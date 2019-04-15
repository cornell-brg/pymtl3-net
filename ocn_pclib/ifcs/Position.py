#=========================================================================
# Position.py
#=========================================================================
# Position formats for different network topologies
#
# Author : Yanghui Ou, Cheng Tan
#   Date : Mar 25, 2019

from pymtl     import *
from BitStruct import mk_bit_struct
import py

#-------------------------------------------------------------------------
# Base MeshPosition
#-------------------------------------------------------------------------

class BaseMeshPosition( object ): 

  def __str__( s ):
    return "({},{})".format( s.pos_x, s.pos_y )

# class MetaMeshPosition( type ):
# 
#   def __new__( meta, name, bases, attrs ):
#     def __new__( cls, mesh_wid, mesh_ht ):
#       XType = mk_bits( clog2( mesh_wid ) )
#       YType = mk_bits( clog2( mesh_ht  ) )
#     
#       def __init__( s, pos_x=0, pos_y=0 ):
#         s.pos_x = XType( pos_x )
#         s.pos_y = YType( pos_y )
#       new_name = "MeshPosition_"+str(mesh_wid)+"_by_"+str(mesh_ht)
#       inst = type( new_name, (), {} )
#       inst.__init__ = __init__
#       return inst
#     attrs['__new__' ] = __new__
#     return type.__new__( meta, name, bases, attrs )
# 
# class mkMeshPosition( BaseMeshPosition ): 
#   __metaclass__ = MetaMeshPosition

#-------------------------------------------------------------------------
# Dynamically generated MeshPosition
#-------------------------------------------------------------------------

_mesh_pos_dict = dict()

#------------------------------------------------------------------------- 
# exec template approach
#------------------------------------------------------------------------- 

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

#------------------------------------------------------------------------- 
# Direct type approach
#------------------------------------------------------------------------- 

# def mk_mesh_pos( mesh_wid, mesh_ht ):
# 
#   if ( mesh_wid, mesh_ht ) in _mesh_pos_dict:
#     return _mesh_pos_dict[ ( mesh_wid, mesh_ht ) ]
# 
#   else:
#     XType = mk_bits( clog2( mesh_wid ) )
#     YType = mk_bits( clog2( mesh_ht  ) )
#     cls_name = "MeshPosition_" + str( mesh_wid ) + "_by_" + str( mesh_ht )
# 
#     def __init__( s, pos_x=0, pos_y=0 ):
#       s.pos_x = XType( pos_x )
#       s.pos_y = YType( pos_y )
# 
#     new_class = type( cls_name, ( BaseMeshPosition, ), {"__init__":__init__} )
#     _mesh_pos_dict[ ( mesh_wid, mesh_ht ) ] = new_class
#     return new_class

#------------------------------------------------------------------------- 
# Metaclass approach
#------------------------------------------------------------------------- 

# def mk_mesh_pos( mesh_wid, mesh_ht ):
# 
#   if ( mesh_wid, mesh_ht ) in _mesh_pos_dict:
#     return _mesh_pos_dict[ ( mesh_wid, mesh_ht ) ]
# 
#   else:
#     class MetaMeshPosition( type ):
#       def __new__( cls, name, bases, attrs ):
#         XType = mk_bits( clog2( mesh_wid ) )
#         YType = mk_bits( clog2( mesh_ht  ) )
#         new_name = "MeshPosition_" + str( mesh_wid ) + "_by_" + str( mesh_ht )
#    
#         def __init__( s, pos_x=0, pos_y=0 ):
#           s.pos_x = XType( pos_x )
#           s.pos_y = YType( pos_y )
# 
#         attrs['__init__'] = __init__
#         return type.__new__( cls, new_name, bases, attrs )
# 
#     class mkMeshPostition( BaseMeshPosition ):
#       __metaclass__ = MetaMeshPosition
# 
#     new_class = mkMeshPostition
#     _mesh_pos_dict[ ( mesh_wid, mesh_ht ) ] = new_class
#     return new_class

#------------------------------------------------------------------------- 
# mk_bistruct approach
#------------------------------------------------------------------------- 
# FIXME: customized __str__ for dynamically generated class?

def mk_mesh_pos( mesh_wid, mesh_ht ):

  if ( mesh_wid, mesh_ht ) in _mesh_pos_dict:
    return _mesh_pos_dict[ ( mesh_wid, mesh_ht ) ]

  else:
    XType = mk_bits( clog2( mesh_wid ) )
    YType = mk_bits( clog2( mesh_ht  ) )
    new_name  = "MeshPosition_" + str( mesh_wid ) + "x" + str( mesh_ht )
    new_class = mk_bit_struct( new_name, {
      'pos_x' : XType,
      'pos_y' : YType
    })
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
class BfPosition_R{row}_N{fly}( object ):
  
  def __init__( s, r = 0, n = 0 ):

    RType = mk_bits( clog2( {row} ) )
    NType = mk_bits( clog2( {fly} ) )

    s.row   = RType( r )
    s.stage = NType( n )

  def __str__( s ):
    return "{{}},{{}}".format( int( s.row ), int( s.stage ) )

_bf_pos_dict[ ( {row}, {fly} ) ] = BfPosition_R{row}_N{fly}
"""

def mk_bf_pos( row, fly ):
  if (row, fly) in _bf_pos_dict:
    return _bf_pos_dict[ ( row, fly ) ]
  else:
    exec py.code.Source( 
      _bf_pos_template.format( row = row, fly = fly ) 
    ).compile() in globals()
    return _bf_pos_dict[ ( row, fly ) ]


#-------------------------------------------------------------------------
# Utility functions
#-------------------------------------------------------------------------

def mk_mesh_pos_list( mesh_wid=2, mesh_ht=2 ):

  pos_list = []

  for c in range( mesh_wid ):
    for r in range( mesh_ht ):
      pos_list.append( mk_mesh_pos( c, r, mesh_wid, mesh_ht ) ) 

  return pos_list
