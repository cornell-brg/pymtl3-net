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
from pymtl3.stdlib.rtl.Encoder import Encoder
from pymtl3.stdlib.ifcs import GetIfcRTL, GiveIfcRTL, SendIfcRTL
from ocnlib.rtl import Counter, GrantHoldArbiter

class SwitchUnitGrantHoldRTL( Component ):

  def construct( s, Type, num_inports=5 ):

    # Local parameters
    s.num_inports = num_inports
    s.Type        = Type
    s.sel_width   = clog2( num_inports )

    # Interface
    s.get  = [ GetIfcRTL( s.Type ) for _ in range( num_inports )  ]
    s.hold = InPort(num_inports)
    s.give = GiveIfcRTL( s.Type )

    # Components
    s.granted_get_rdy = Wire()
    s.any_hold        = Wire()

    s.arbiter = GrantHoldArbiter( nreqs=num_inports )
    s.arbiter.hold //= s.any_hold

    s.mux = Mux( s.Type, num_inports )
    s.mux.out //= s.give.ret

    s.encoder = m = Encoder( num_inports, s.sel_width )
    m.in_ //= s.arbiter.grants
    m.out //= s.mux.sel

    # Combinational Logic
    @update
    def up_any_hold():
      s.any_hold @= s.hold > 0

    @update
    def up_granted_get_rdy():
      s.granted_get_rdy @= 0
      for i in range( num_inports ):
        if s.arbiter.grants[i]:
          s.granted_get_rdy @= s.get[i].rdy

    for i in range( num_inports ):
      s.get[i].rdy //= s.arbiter.reqs[i]
      s.get[i].ret //= s.mux.in_[i]

    for i in range( num_inports ):
      s.get[i].en //= lambda: s.give.en & ( s.mux.sel == i )

    s.give.rdy //= s.granted_get_rdy

  def line_trace( s ):
    in_trace  = '|'.join( [ str(p) for p in s.get ] )
    hold      = ''.join([ '^' if h else '.' for h in s.hold ])
    out_trace = f'{s.give}'
    return f'{in_trace}({hold}){out_trace}'

