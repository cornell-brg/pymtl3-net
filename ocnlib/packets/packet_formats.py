'''
==========================================================================
packet_format.py
==========================================================================
Base class for format definition of multi-flit packet.

Author : Yanghui Ou
  Date : Jan 29, 2020
'''

_FIELDS = '__packet_format__'

#-------------------------------------------------------------------------
# _check_format_field
#-------------------------------------------------------------------------
# Check if a field annotation is valid.

def _check_format_field( fname, t ):
  flag = True
  flag &= isinstance( t, tuple )
  flag &= len( t ) == 2
  lo, hi = t
  flag &= ( isinstance( lo, int ) and isinstance( hi, int ) )

  if not flag:
    raise AttributeError( f'Field {fname} should be annotated with a tuple of two int!' )

  if lo > hi:
    raise AttributeError( f'Field {fname}: first int should not be greater than the second!' )

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

def packet_format( cls ):
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
    _check_format_field( fname, tpl )
    lo, hi = tpl
    slice_dict[ fname ] = slice( lo, hi )

  setattr( cls, _FIELDS, slice_dict )

  # Set variables
  for fname, slice in slice_dict.items():
    setattr( cls, fname, slice )

  return cls

# TODO: mk_packet_format
# Yanghui: currently I do not think a `mk_packet_format` is very useful.
# If it turns out there are some use cases for it then I will come back
# and implement it.

