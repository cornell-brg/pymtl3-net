'''
==========================================================================
connects.py
==========================================================================
Collection of customized connects.

Author : Yanghui Ou
  Date : Jan 29, 2020
'''
from pymtl3 import *
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

