'''
==========================================================================
GrantHoldArbiter.py
==========================================================================
A round-robin arbiter with grant-hold circuit.

Author : Yanghui Ou
  Date : Jan 22, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.rtl.arbiters import RoundRobinArbiterEn


class GrantHoldArbiter( Component ):

  def construct( s, nreqs ):
    BitsN = mk_bits( nreqs )

    # Interface
    s.reqs   = InPort ( BitsN )
    s.hold   = InPort ( Bits1 )
    s.en     = InPort ( Bits1 )
    s.grants = OutPort( BitsN )

    # Components
    s.arb    = RoundRobinArbiterEn( nreqs )
    s.last_r = Wire( BitsN )
    s.hold_r = Wire( Bits1 )

    # Logic
    s.arb.en   //= s.en
    s.arb.reqs //= lambda: BitsN(0) if s.hold else s.reqs
    s.grants   //= lambda: s.arb.grants if ~s.hold else s.last_r

    @s.update_ff
    def up_r():
      s.last_r <<= s.grants
      s.hold_r <<= s.hold
    
  def line_trace( s ):
    hold = 'h' if s.hold else ' '
    en   = 'e' if s.arb.en else ' '
    arb  = f'{s.arb.priority_reg.out.bin()[2:]}'
    return f'{str(s.reqs.bin())[2:]}({hold}|{en}|{arb}){str(s.grants.bin())[2:]}'
