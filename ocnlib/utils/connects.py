'''
==========================================================================
connects.py
==========================================================================
Collection of customized connects.

Author : Yanghui Ou
  Date : Jan 29, 2020
'''
from pymtl3 import *
from pymtl3.datatypes.bitstructs import (
  is_bitstruct_class, 
  _FIELDS as bitstruct_fields,
)

#------------------------------------------------------------------------- 
# bitstruct_to_slice_h
#------------------------------------------------------------------------- 
# Recursive helper function

def _bitstruct_to_slices_h( cls, slices ): 
  if issubclass( cls, Bits ):
    start = 0 if not slices else slices[-1].stop
    stop  = start + cls.nbits
    slices.append( slice( start, stop ) )

  else:
    assert is_bitstruct_class( cls )
    fields_dict = getattr( cls, bitstruct_fields )
    fields_lst  = list( fields_dict.items() )
    # Use reverse instead of [::-1] because it is faster
    fields_lst.reverse()
    for _, ftype in fields_lst:
      _bitstruct_to_slices_h( ftype, slices )

#------------------------------------------------------------------------- 
# bitstruct_to_slice
#------------------------------------------------------------------------- 
# Converts a bitstruct to a list of slices
# TODO: import this from commons.py

def bitstruct_to_slices( cls ):
  slices = []
  _bitstruct_to_slices_h( cls, slices )
  return slices

#------------------------------------------------------------------------- 
# _connect_bitstruct_h
#------------------------------------------------------------------------- 

def _connect_bitstruct_h( field, bits_signal, slices ): 
  field_type = field._dsl.Type

  if issubclass( field_type, Bits ):
    start     = 0 if not slices else slices[-1].stop
    stop      = start + field_type.nbits
    cur_slice = slice( start, stop )
    slices.append( cur_slice )
    connect( field, bits_signal[ cur_slice ] )

  else:
    assert is_bitstruct_class( field_type )
    fields_dict = getattr( field_type, bitstruct_fields )
    fields_lst  = list( fields_dict.items() )
    # Use reverse instead of [::-1] because it is faster
    fields_lst.reverse()
    for fname, _ in fields_lst:
      subfield = getattr( field, fname )
      _connect_bitstruct_h( subfield, bits_signal, slices )

#------------------------------------------------------------------------- 
# connect_bitstruct
#------------------------------------------------------------------------- 

def connect_bitstruct( signal1, signal2 ):
  type1 = signal1._dsl.Type
  type2 = signal2._dsl.Type

  if is_bitstruct_class( type1 ):
    assert issubclass( type2, Bits )
    bits_signal, bitstruct_signal = signal2, signal1
  elif is_bitstruct_class( type2 ):
    assert issubclass( type1, Bits )
    bits_signal, bitstruct_signal = signal1, signal2
  else:
    assert False, "Can only connect a bitstruct wire to bits wire"

  # Connect field to corresponding slice
  _connect_bitstruct_h( bitstruct_signal, bits_signal, [] )


