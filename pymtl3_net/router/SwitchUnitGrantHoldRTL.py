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
from pymtl3.stdlib.primitive import Mux, Encoder
# from pymtl3.stdlib.ifcs import GetIfcRTL, GiveIfcRTL, OStreamIfc
from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc
from pymtl3_net.ocnlib.rtl import Counter, GrantHoldArbiter

class SwitchUnitGrantHoldRTL( Component ):

  def construct( s, Type, num_inports=5 ):

    # Local parameters
    s.num_inports = num_inports
    s.Type        = Type
    s.sel_width   = clog2( num_inports )

    # Interface
    s.recv = [ IStreamIfc( s.Type ) for _ in range( num_inports )  ]
    s.hold = InPort(num_inports)
    s.send = OStreamIfc( s.Type )

    # Components
    s.granted_recv_val = Wire()
    s.any_hold        = Wire()

    s.arbiter = GrantHoldArbiter( nreqs=num_inports )
    s.arbiter.hold //= s.any_hold
    s.arbiter.en   //= lambda: ~s.any_hold & s.send.val & s.send.rdy

    s.mux = Mux( s.Type, num_inports )
    s.mux.out //= s.send.msg

    s.encoder = Encoder( num_inports, s.sel_width )
    s.encoder.in_  //= s.arbiter.grants
    s.encoder.out  //= s.mux.sel

    # Combinational Logic
    @update
    def up_any_hold():
      s.any_hold @= s.hold > 0

    @update
    def up_granted_get_rdy():
      s.granted_recv_val @= 0
      for i in range( num_inports ):
        if s.arbiter.grants[i]:
          s.granted_recv_val @= s.recv[i].val

    for i in range( num_inports ):
      s.recv[i].val //= s.arbiter.reqs[i]
      s.recv[i].msg //= s.mux.in_[i]

    for i in range( num_inports ):
      s.recv[i].rdy //= lambda: s.send.rdy & ( s.mux.sel == i )

    s.send.val //= s.granted_recv_val

  def line_trace( s ):
    in_trace  = '|'.join( [ str(p) for p in s.recv ] )
    hold      = ''.join([ '^' if h else '.' for h in s.hold ])
    out_trace = f'{s.send}'
    return f'{in_trace}({hold}){out_trace}'

