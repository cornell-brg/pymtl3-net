'''
==========================================================================
connects.py
==========================================================================
Collection of customized connects.

Author : Yanghui Ou
  Date : Jan 29, 2020
'''
from pymtl3 import *
from pymtl3.datatypes.bitstructs import is_bitstruct_class, _FIELDS as bitstruct_fields
from ..packets.packet_formats import _FIELDS

#------------------------------------------------------------------------- 
# _name_mangle
#------------------------------------------------------------------------- 
# Flattens a dsl name so that it can be used for creating new signals.
# TODO: list?

def _name_mangle( dsl_name ):
  name = dsl_name.replace( '[', '' ).replace( ']', '' )
  lst = name.split( '.' )[1:] # get rid of s.
  return '_'.join( lst ) 

#------------------------------------------------------------------------- 
# connect_format
#------------------------------------------------------------------------- 
# Automatically create wires from a packet format and connect them to the
# corresponding slices.

def connect_format( host, Format, signal ):
  slice_dict = Format.__dict__[ _FIELDS ]
  for fname, fslice in slice_dict.items():
    # Generate a new name
    new_name = _name_mangle( signal._dsl.full_name ) + f'_{fname}'
    if hasattr( host, new_name ):
      raise AttributeError( f'Failed to add a new wire! {host} already has an attribute called {new_name}!' )

    # Create a new wire and add it to host
    bitwidth = fslice.stop - fslice.start
    new_wire = Wire( mk_bits( bitwidth ) )
    print( f'setting {new_name} to {host}' )
    setattr( host, new_name, new_wire )
    connect( new_wire, signal[ fslice ] )

#------------------------------------------------------------------------- 
# connect_union_wire
#------------------------------------------------------------------------- 
# Automatically create a bitstruct for a packet format and adds a wire to
# the component.
# NOTE: The argument [signal] must has type of Bits.
# NOTE: We can also create a new level of Component that has this function
# as a method.

def connect_union( host, Format, wire_name, signal ):
  slice_dict  = Format.__dict__[ _FIELDS ]
  field_dict  = { fname : mk_bits( fslice.stop - fslice.start ) for fname, fslice in slice_dict.items() }

  # FIXME: Possible name confilct if two formats in different modules
  # have the same name.
  struct_name = f'{Format.__name__}Struct'
  StructType  = mk_bitstruct( f'', field_dict )
  new_wire    = Wire( StructType )

  # Add the new wire to host
  setattr( host, wire_name, new_wire )

  # Connect each field to the corresponding slice
  for fname, fslice in slice_dict.items():
    connect( getattr( new_wire, fname ), signal[ fslice ] )


#------------------------------------------------------------------------- 
# _get_bitstruct_nbits
#------------------------------------------------------------------------- 

def _get_bitstruct_nbits_h( cls, acc ): 
  if issubclass( cls, Bits ):
    return cls.nbits

  else:
    assert is_bitstruct_class( cls )
    fields = getattr( cls, bitstruct_fields )

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
    fields = getattr( cls, bitstruct_fields )
    for _, ftype in fields.items():
      _bitstruct_to_slices_h( ftype, slices )

#------------------------------------------------------------------------- 
# bitstruct_to_slice_h
#------------------------------------------------------------------------- 
# Converts a bitstruct to a list of slices

def _bitstruct_to_slices( cls ):
  slices = []
  _bitstruct_to_slices( cls, slices )
      
#------------------------------------------------------------------------- 
# connect_union_wire
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

