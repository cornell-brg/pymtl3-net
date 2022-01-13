'''
==========================================================================
MflitPacket.py
==========================================================================
A **non translatable** data type that helps testing components that use
multi-flit (single-phit flit) packets.

Author : Yanghui Ou
  Date : Jan 31, 2019
'''
from pymtl3 import mk_bits
from pymtl3.datatypes.bitstructs import (
  is_bitstruct_class,
  _FIELDS as bitstruct_fields,
)

#-------------------------------------------------------------------------
# _get_payload_length
#-------------------------------------------------------------------------

def _get_payload_length( Format, header_flit, field_name='plen' ):
  header = Format.from_bits( header_flit )
  return getattr( header, field_name ).uint()

#-------------------------------------------------------------------------
# MflitPacket
#-------------------------------------------------------------------------

class MflitPacket:

  def __init__( self, Format, flits=[], plen_field_name='plen' ):

    self.Format     = Format
    self.plen_fname = plen_field_name
    self.PhitType   = mk_bits( Format.nbits )
    self.add_lock   = False
    self.pop_lock   = False
    self.nflits     = 0
    self.flit_idx   = 0
    self.flits      = [ self.PhitType(f) for f in flits ]

    # Check
    if self.flits:
      self._get_nflits()
      assert self.nflits == len( self.flits )

  def add( self, flit ):
    assert not self.pop_lock, "Packet locked by pop, cannot add any more!"

    # Adding header flit
    if self.empty():
      self.flits.append( flit )
      self._get_nflits()
    else:
      assert not self.full(), "Packet is already full"
      self.flits.append( flit )

    self.add_lock = True

  def pop( self ):
    assert not self.add_lock, "Packet locked by add, cannot pop any more!"
    assert self.flit_idx < self.nflits, "Already reached the last flit of the packet!"
    # Copy the current flit
    cur_flit = self.PhitType( self.flits[ self.flit_idx ] )

    self.flit_idx += 1
    self.pop_lock = True
    return cur_flit

  def full( self ):
    return self.nflits > 0 and self.nflits == len( self.flits ) and self.flit_idx == 0

  def empty( self ):
    return len( self.flits ) == 0 or self.flit_idx == self.nflits

  def _get_nflits( self ):
    nflits = _get_payload_length( self.Format, self.flits[0], self.plen_fname ) + 1
    self.nflits = nflits
