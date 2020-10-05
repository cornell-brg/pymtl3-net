'''
==========================================================================
SwitchUnitGrantHoldValRdy.py
==========================================================================
Switch unit that supports multi-flit (single-phit flit) packet.

R.I.P. Kobe.

Author : Yanghui Ou
  Date : Oct 5, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.basic_rtl import Mux, Encoder
from pymtl3.stdlib.ifcs import InValRdyIfc, OutValRdyIfc
from ocnlib.rtl import Counter, GrantHoldArbiter

class SwitchUnitGrantHoldValRdy( Component ):

  def construct( s, Type, num_inports=5 ):

    # Local parameters
    s.num_inports = num_inports
    s.Type        = Type
    s.sel_width   = clog2( num_inports )

    # Interface
    s.in_  = [ InValRdyIfc( s.Type ) for _ in range( num_inports )  ]
    s.hold = InPort( num_inports )
    s.out  = OutValRdyIfc( s.Type )

    # Components
    s.granted_out_val = Wire()
    s.any_hold        = Wire()

    s.arbiter = GrantHoldArbiter( nreqs=num_inports )
    s.arbiter.hold //= s.any_hold
    s.arbiter.en   //= lambda: ~s.any_hold & s.out.val & s.out.rdy

    s.mux = Mux( s.Type, num_inports )
    s.mux.out //= s.out.msg

    s.encoder = Encoder( num_inports, s.sel_width )
    s.encoder.in_  //= s.arbiter.grants
    s.encoder.out  //= s.mux.sel

    # Combinational Logic
    @update
    def up_any_hold():
      s.any_hold @= s.hold > 0

    @update
    def up_granted_out_val():
      s.granted_out_val @= 0
      for i in range( num_inports ):
        if s.arbiter.grants[i]:
          s.granted_out_val @= s.in_[i].val

    for i in range( num_inports ):
      s.in_[i].val //= s.arbiter.reqs[i]
      s.in_[i].msg //= s.mux.in_[i]

    for i in range( num_inports ):
      s.in_[i].rdy //= lambda: s.out.rdy & ( s.mux.sel == i )

    s.out.val //= s.granted_out_val

  def line_trace( s ):
    in_trace  = '|'.join( [ str(p) for p in s.in_ ] )
    hold      = ''.join([ '^' if h else '.' for h in s.hold ])
    out_trace = f'{s.out}'
    return f'{in_trace}({hold}){out_trace}'
