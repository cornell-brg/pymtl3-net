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
# run_sim
#-------------------------------------------------------------------------
# A generic run_sim function

def run_sim( th, max_cycles=1000, translation='',
             dut_name='dut', vl_trace=False, xinit='zeros' ):

  th.elaborate()

  if translation == 'verilog':
    from pymtl3.passes.backends.verilog import TranslationImportPass

    dut = getattr( th, dut_name )
    dut.set_metadata( TranslationImportPass.enable, True )
    dut.set_metadata( VerilatorImportPass.vl_xinit, xinit )
    dut.set_metadata( VerilatorImportPass.vl_trace, vl_trace )

  elif translation == 'yosys':
    from pymtl3.passes.backends.yosys import TranslationImportPass

    dut = getattr( th, dut_name )
    dut.set_metadata( TranslationImportPass.enable, True )
    dut.set_metadata( VerilatorImportPass.vl_xinit, xinit )
    dut.set_metadata( VerilatorImportPass.vl_trace, vl_trace )

  elif translation:
    assert False, f'Invalid translation backend {translation}!'

  if translation:
    th = TranslationImportPass()( th )
    th.elaborate()

  th.apply( SimulationPass(print_line_trace=True) )
  th.sim_reset()

  # Run simulation
  while not th.done() and th.sim_cycle_count() < max_cycles:
    th.sim_tick()

  # Check timeout
  assert th.sim_cycle_count() < max_cycles

  th.sim_tick()
  th.sim_tick()
  th.sim_tick()
