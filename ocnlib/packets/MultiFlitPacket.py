'''
==========================================================================
MultiFlitPacket.py
==========================================================================
A **non translatable** data type that helps testing components that use
multi-flit (single-phit flit) packets.

Author : Yanghui Ou
  Date : Jan 31, 2019
'''

#-------------------------------------------------------------------------
# _get_payload_length
#-------------------------------------------------------------------------

def _get_payload_length( Format, header_flit, field_name='plen' ):
  plen_slice = getattr( Format, plen_field_name )
  return header[ plen_slice ].uint()

#-------------------------------------------------------------------------
# MultiFlitPacket
#-------------------------------------------------------------------------

class MultiFlitPacket:

  def __init__( self, Format, flits=[], plen_field_name='plen' ):

    self.PhitType = Format.PhitType
    self.add_lock = False
    self.pop_lock = False
    self.nflits   = 0
    self.flit_idx = 0
    self.flits    = [ self.PhitType(f) for f in flits ]

    # Check
    if self.flits:
      self._get_nflits()

  def add( self, flit ):
    assert not pop_lock, "Packet locked by pop, cannot add any more!"

    # Adding header flit
    if self.empty():
      self.flits.append( flits )
      self._get_nflits()
    else:
      assert not self.full(), "Packet is already full" 
      self.flits.append( flits )

    self.add_lock = True

  def pop( self ):
    assert not add_lock, "Packet locked by add, cannot pop any more!"
    assert self.flit_idx < self.nflits "Already reached the last flit of the packet!" 
    # Copy the current flit
    cur_flit = self.PhitType( self.flits[ self.flit_idx ] )

    self.flit_idx += 1
    self.pop_lock = True
    return cur_flit

  def full( self ):
    return s.nflits > 0 and s.nflits == len( self.flits )

  def empty( self ):
    return len( self.flits == 0 ) 

  def _get_nflits( self ):
    nflits = _get_payload_length( Format, self.flits[0], plen_field_name )
    assert nflits == len( self.flits ) - 1
    self.nflits = nflits
