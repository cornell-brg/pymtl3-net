#=========================================================================
# BitStruct.py
#=========================================================================
# A base BitStruct definition.
# 
# Author : Yanghui Ou
#   Date : Apr 8, 2019

from pymtl       import *
from collections import OrderedDict
import py
import copy

class BitStruct( object ):

  # Default line trace
  def __str__( s ):
    trace = ""
    #for name, value in vars( s ).items():
    for name, _ in s.fields:
      trace += "{}:".format( vars( s )[name] )
    return trace[:-1]
  
  @classmethod
  def copy( cls, inst ):
    if isinstance( inst, cls ):
      # Is deep copy necessary?
      return copy.deepcopy( inst )
    else:
      raise AssertionError( "Cannot construct {{}} from {{}}!" ).format(
        cls.__name__, type( inst ) )

  def line_trace( s ):
    return s.__str__()

#-------------------------------------------------------------------------
# Dynamically generate bit struct
#-------------------------------------------------------------------------

_struct_dict = dict()
_fields_dict = dict()
_struct_tmpl = """
class {name}( BitStruct ):

  def __init__( s, {args_str} ):
{assign_str}

_struct_dict[\"{name}\"] = {name}
"""

# def mk_bit_struct( name, fields ):
#   
#   # TODO: check invalid keywords
#   def __init__( s, *args, **kwargs ):
# 
#     od = OrderedDict( fields )
#     # handle positional arguments
#     for value in args:
#       field_name, FieldType = od.popitem(False)
#       setattr( s, field_name, FieldType( value ) )
# 
#     # handle keyword arguments
#     for field_name, FieldType in od.items():
#       if field_name in kwargs:
#         setattr( s, field_name, FieldType( kwargs[field_name] ) )
#       else:
#         setattr( s, field_name, FieldType( 0 ) )
# 
#   return type( name, ( BitStruct, ), { '__init__' : __init__ } ) 

# FIXME: assert not working. 
def mk_bit_struct( name, fields, str_func=None ):

  if name in _struct_dict:
    if _fields_dict[name] == fields:
      return _struct_dict[name]
    else:
      raise AssertionError(
        "BitStruct {} has already been created!".format( name ) )
  else:
    args_str   = ""
    assert_str = ""
    assign_str = ""
    # FIXME: order is screwed
    for field_name, FieldType in fields:
      # if not isinstance( FieldType(), BitStruct ):
      #   args_str   += "{}=0, ".format( field_name )
      #   assign_str += "    s.{} = {}( {} )\n".format( 
      #     field_name, FieldType.__name__, field_name )
      # else:
      #   args_str   += "{}={}(), ".format( field_name, FieldType.__name__ )
      #   assign_str += "    s.{} = {}.copy( {} )\n".format( 
      #     field_name, FieldType.__name__, field_name )
      args_str   += "{}={}(), ".format( field_name, FieldType.__name__ )
      assert_str += "    assert isinstance( {}, {} )\n".format( field_name, FieldType.__name__ ) 
      assign_str += "    s.{} = {}\n".format( field_name, field_name )
    args_str = args_str[:-2]

    print _struct_tmpl.format( **locals() )
    exec py.code.Source(
      _struct_tmpl.format( **locals() )
    ).compile() in globals()

    cls = _struct_dict[name]
    cls.fields = fields
    if str_func is not None:
      cls.__str__ = str_func

    _fields_dict[name] = fields
    return _struct_dict[name]

# class CustomizedPoint( 
#   mk_bit_struct( "BasePoint", OrderedDict({
#     'x' : Bits16,
#     'y' : Bits16
#    }) ) ):
# 
#   def __str__( s ):
#     return "({},{})".format( int(s.x), int(s.y) )
# 
# def test_struct():
# 
#   pt = CustomizedPoint( Bits16(2), Bits16(4) )
#   print pt
#   
#   NestedSimple = mk_bit_struct( "NestedSimple", OrderedDict({
#     'pt0' : CustomizedPoint,
#     'pt1' : CustomizedPoint
#   }) )
# 
#   print NestedSimple 
#   print NestedSimple( CustomizedPoint(1,1), CustomizedPoint(2,2) )
# 
#   def dynamic_point( xnbits, ynbits ):
#     XType = mk_bits( xnbits )
#     YType = mk_bits( ynbits )
# 
#     return mk_bit_struct( 
#       "Point_{}_{}".format( xnbits, ynbits ), OrderedDict({
#         'x': XType,
#         'y': YType
#       }),
#       lambda s: "({},{})".format( int(s.x), int(s.y) )
#     )
#     
#   DPoint = dynamic_point( 4, 4 )
#   print DPoint
#   dp = DPoint( 1, 1 )
#   print dp

