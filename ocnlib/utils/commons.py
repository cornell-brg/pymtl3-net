'''
==========================================================================
commons.py
==========================================================================
Common utility functions.

Author : Yanghui Ou
  Date : Feb 9, 2020
'''
from functools import reduce
from pymtl3 import *
from pymtl3.datatypes.bitstructs import(
  is_bitstruct_class,
  is_bitstruct_inst,
  _FIELDS as bitstruct_fields,
)

#-------------------------------------------------------------------------
# get_nbits
#-------------------------------------------------------------------------
# TODO: support instance too

def get_nbits( cls ):
  if issubclass( cls, Bits ):
    return cls.nbits

  else:
    assert is_bitstruct_class( cls )
    fields_dict = getattr( cls, bitstruct_fields )
    total_nbits = 0
    for _, ftype in fields_dict.items():
      total_nbits +=  get_nbits( ftype )
    return total_nbits

#-------------------------------------------------------------------------
# get_plen_type
#-------------------------------------------------------------------------
# Returns the type of feild payload length from the header format.
# FIXME: hacky.

def get_plen_type( cls, plen_field_name='plen' ):
  assert is_bitstruct_class( cls )
  fields_dict = getattr( cls, bitstruct_fields )

  if not plen_field_name in fields_dict:
    raise AssertionError( f'{cls.__qualname__} does not have field {plen_field_name}!' )

  return fields_dict[ plen_field_name ]

#-------------------------------------------------------------------------
# get_field_type( cls ):
#-------------------------------------------------------------------------

def get_field_type( cls, field_name ):
  assert is_bitstruct_class( cls )
  fields_dict = getattr( cls, bitstruct_fields )

  if not field_name in fields_dict:
    raise AssertionError( f'{cls.__qualname__} does not have field {field_name}!' )

  return fields_dict[ field_name ]

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

def bitstruct_to_slices( cls ):
  slices = []
  _bitstruct_to_slices_h( cls, slices )
  return slices

#-------------------------------------------------------------------------
# to_bits
#-------------------------------------------------------------------------
# Converts a bitstruct object to bits

def to_bits( obj ):
  if isinstance( obj, Bits ):
    # FIXME: call clone here once pymtl3 is updated
    return obj.__class__( obj )

  else:
    assert is_bitstruct_inst( obj )
    fields_dict = getattr( obj, bitstruct_fields )

    acc = []
    for fname, ftype in fields_dict.items():
      bits = to_bits( getattr( obj, fname ) )
      acc.append( bits )

    return reduce( lambda a, b: concat( a, b ), acc )

#-------------------------------------------------------------------------
# _to_bitstruct_h
#-------------------------------------------------------------------------
# Recursive helper function for to_bitstruct.
# NOTE: I am being very conservative here to copy every field.

def _to_bitstruct_h( field_type, bits_obj, slices_stack ):
  if issubclass( field_type, Bits ):
    cur_slice = slices_stack.pop()
    return field_type( bits_obj[ cur_slice ] )

  else:
    assert is_bitstruct_class( field_type )
    ret = field_type()
    fields_dict = getattr( field_type, bitstruct_fields )
    for fname, ftype in fields_dict.items():
      field_value = _to_bitstruct_h( ftype, bits_obj, slices_stack )
      setattr( ret, fname, field_value )
    return ret

#-------------------------------------------------------------------------
# to_bitstruct
#-------------------------------------------------------------------------
# Converts a bit or bitstruct object to bitstruct
# TODO: more informative error message.

def to_bitstruct( obj, BitstructType ):
  bits_obj = to_bits( obj )
  assert isinstance( bits_obj, Bits )

  slices_stack = bitstruct_to_slices( BitstructType )
  assert bits_obj.nbits == slices_stack[-1].stop, "Bit width mismatch!"
  ret = _to_bitstruct_h( BitstructType, bits_obj, slices_stack )
  assert not slices_stack # Make sure every field is assigned
  return ret

#-------------------------------------------------------------------------
# run_sim
#-------------------------------------------------------------------------
# A generic run_sim function

def run_sim( th, max_cycles=1000, translation='', 
             dut_name='dut', vl_trace=False, xinit='zeros' ):

  th.elaborate()

  if translation == 'verilog':
    from pymtl3.passes.backends.verilog import TranslationImportPass
    from pymtl3.passes.backends.verilog import VerilatorImportConfigs
    getattr( th, dut_name ).verilog_translate_import = True
    getattr( th, dut_name ).config_verilog_import = VerilatorImportConfigs(
      vl_trace = vl_trace,
      vl_xinit = xinit,
    )

  elif translation == 'yosys':
    from pymtl3.passes.backends.yosys import TranslationImportPass
    from pymtl3.passes.backends.yosys import VerilatorImportConfigs
    getattr( th, dut_name ).yosys_translate_import = True
    getattr( th, dut_name ).config_yosys_import = VerilatorImportConfigs(
      vl_trace = vl_trace,
      vl_xinit = xinit,
    )

  elif translation:
    assert False, f'Invalid translation backend {translation}!'

  if translation:
    th = TranslationImportPass()( th )
    th.elaborate()

  th.apply( SimulationPass() )
  th.sim_reset()

  # Run simulation
  print()
  th.print_line_trace()
  while not th.done() and th.simulated_cycles < max_cycles:
    th.tick()
    th.print_line_trace()

  # Check timeout
  assert th.simulated_cycles < max_cycles
  th.tick()
  th.tick()
  th.tick()
