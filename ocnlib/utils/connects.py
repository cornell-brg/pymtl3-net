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

