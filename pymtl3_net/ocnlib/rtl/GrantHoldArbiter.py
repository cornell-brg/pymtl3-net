'''
==========================================================================
GrantHoldArbiter.py
==========================================================================
A round-robin arbiter with grant-hold circuit.

Author : Yanghui Ou
  Date : Jan 22, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.basic_rtl import RoundRobinArbiterEn


class GrantHoldArbiter( Component ):

  def construct( s, nreqs ):

    # Interface
    s.reqs   = InPort ( nreqs ) 
    s.grants = OutPort( nreqs )
    s.hold   = InPort ()
    s.en     = InPort ()

    # Components
    s.arb    = RoundRobinArbiterEn( nreqs )
    s.last_r = Wire( nreqs )

    # Logic
    s.arb.reqs //= lambda: 0 if s.hold else s.reqs
    s.arb.en   //= lambda: s.en
    s.grants   //= lambda: s.arb.grants if ~s.hold else s.last_r

    @update_ff
    def up_last_r():
      s.last_r <<= s.grants

  def line_trace( s ):
    hold = 'h' if s.hold else ' '
    en   = 'e' if s.arb.en else ' '
    arb  = f'{s.arb.priority_reg.out.bin()[2:]}'
    return f'{str(s.reqs.bin())[2:]}({hold}|{en}|{arb}){str(s.grants.bin())[2:]}'
