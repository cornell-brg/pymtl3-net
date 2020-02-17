'''
==========================================================================
SwitchUnitGrantHoldRTL.py
==========================================================================
Switch unit that supports multi-flit (single-phit flit) packet.

R.I.P. Kobe.

Author : Yanghui Ou
  Date : Jan 26, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.rtl import Mux
# FIXME: pymtl3.stdlib.rtl.Encoder
from pymtl3.stdlib.rtl.Encoder import Encoder
from pymtl3.stdlib.ifcs import GetIfcRTL, GiveIfcRTL, SendIfcRTL
from ocnlib.rtl import Counter, GrantHoldArbiter
from ocnlib.utils.connects import connect_union


class SwitchUnitGrantHoldRTL( Component ):

  def construct( s, Type, num_inports=5 ):

    # Local parameters
    s.num_inports = num_inports
    s.Type        = Type
    s.sel_width   = clog2( num_inports )

    GrantType     = mk_bits( num_inports )
    SelType       = mk_bits( s.sel_width )

    # Interface
    s.get  = [ GetIfcRTL( s.Type ) for _ in range( num_inports )  ]
    s.hold = [ InPort( Bits1 ) for _ in range( num_inports ) ]
    s.give = GiveIfcRTL( s.Type )

    # Components
    s.granted_get_rdy = Wire( Bits1 )
    s.any_hold        = Wire( Bits1 )

    s.arbiter = GrantHoldArbiter( nreqs=num_inports )( hold = s.any_hold )
    s.mux     = Mux( s.Type, num_inports )( out = s.give.ret )
    s.encoder = Encoder( num_inports, s.sel_width )(
      in_ = s.arbiter.grants,
      out = s.mux.sel,
    )

    # Combinational Logic
    @s.update
    def up_any_hold():
      s.any_hold = b1(0)
      for i in range( num_inports ):
        if s.hold[i]:
          s.any_hold = b1(1)

    @s.update
    def up_granted_get_rdy():
      s.granted_get_rdy = b1(0)
      for i in range( num_inports ):
        if s.arbiter.grants[i]:
          s.granted_get_rdy = s.get[i].rdy

    for i in range( num_inports ):
      s.get[i].rdy //= s.arbiter.reqs[i]
      s.get[i].ret //= s.mux.in_[i]

    @s.update
    def up_get_en():
      for i in range( num_inports ):
        s.get[i].en = s.give.en & ( s.mux.sel == SelType(i) )

    # FIXME: use the lambda syntax after updating pymtl3 which fix the
    # transalation bug
    # for i in range( num_inports ):
    #   s.get[i].en //= lambda: s.give.en & ( s.mux.sel == SelType(i) )

    s.give.rdy //= s.granted_get_rdy

  def line_trace( s ):
    in_trace  = '|'.join( [ str(p) for p in s.get ] )
    hold      = ''.join([ '^' if h else '.' for h in s.hold ])
    out_trace = f'{s.give}'
    return f'{in_trace}({hold}){out_trace}'

