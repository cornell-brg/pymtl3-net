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

    # Interface
    s.reqs   = InPort ( nreqs )
    s.grants = OutPort( nreqs )
    s.hold   = InPort ()

    # Components
    s.arb    = RoundRobinArbiterEn( nreqs )
    s.last_r = Wire( nreqs )

    # Logic
    s.arb.reqs //= lambda: 0 if s.hold else s.reqs
    s.arb.en   //= lambda: ~s.hold
    s.grants   //= lambda: s.arb.grants if ~s.hold else s.last_r

    @update_ff
    def up_last_r():
      s.last_r <<= s.grants

  def line_trace( s ):
    hold = 'h' if s.hold else ' '
    return f'{str(s.reqs.bin())[2:]}({hold}){str(s.grants.bin())[2:]}'
