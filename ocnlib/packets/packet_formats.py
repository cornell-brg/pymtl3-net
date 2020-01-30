'''
==========================================================================
packet_format.py
==========================================================================
Base class for format definition of multi-flit packet.

Author : Yanghui Ou
  Date : Jan 29, 2020
'''
from pymtl3 import mk_bits

_FIELDS    = '__packet_format__'
_PHIT_TYPE = 'PhitType'

#-------------------------------------------------------------------------
# _check_format_field
#-------------------------------------------------------------------------
# Check if a field annotation is valid.

def _check_format_field( fname, t, width ):
  if fname == _PHIT_TYPE:
    raise AttributeError( f'Cannot have a filed named {_PHIT_TYPE}! It is reserved.' )
  flag = True
  flag &= isinstance( t, tuple )
  flag &= len( t ) == 2
  lo, hi = t
  flag &= ( isinstance( lo, int ) and isinstance( hi, int ) )

  if not flag:
    raise AttributeError( f'Field {fname} should be annotated with a tuple of two int!' )

  if lo > hi:
    raise AttributeError( f'Field {fname}: first int should not be greater than the second!' )

  if hi > width:
    raise AssertionError( f'Field {fname} exceeds the maximum bitwidth.' )

#-------------------------------------------------------------------------
# packet_format
#-------------------------------------------------------------------------
# Class decorator that turns a class into a packet format definition.
# For example:
# 
# class PitonFormat:
#   # Field  LO  HI   
#   CHIPID:  50, 64 
#   XPOS  :  42, 50 
#   YPOS  :  34, 42

def packet_format( phit_width ):

  def _process_class( cls ): 
    global slice
    # get annotations of the class
    cls_annotations = cls.__dict__.get( '__annotations__', {} )
    if not cls_annotations:
      raise AttributeError( 
        'No field is declared in the packet format definition. ' 
        f'Please check the definition of {cls.__qualname__}.'
      )

    # Generate slice objects
    slice_dict = {}
    for fname, tpl in cls_annotations.items():
      _check_format_field( fname, tpl, phit_width )
      lo, hi = tpl
      slice_dict[ fname ] = slice( lo, hi )

    setattr( cls, _FIELDS, slice_dict )

    # Set variables
    for fname, fslice in slice_dict.items():
      setattr( cls, fname, fslice )

    setattr( cls, _PHIT_TYPE, mk_bits( phit_width ) )

    return cls

  return _process_class

# TODO: mk_packet_format
# Yanghui: currently I do not think a `mk_packet_format` is very useful.
# If it turns out there are some use cases for it then I will come back
# and implement it.

