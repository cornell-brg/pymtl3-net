'''
==========================================================================
SwitchUnitMFlitRTL.py
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
from ocnlib.utils.connects import connect_format


class SwitchUnitMFlitRTL( Component ):

  def construct( s, HeaderFormat, num_inports=5 ):

    # Local parameters
    # NOTE: FlitType must be a BitsN type
    # TODO: check for slice object
    PLEN            = HeaderFormat.PLEN
    FlitType        = HeaderFormat.PhitType
    s.STATE_HEADER  = b1(0)
    s.STATE_BODY    = b1(1)
    s.header_format = HeaderFormat
    s.num_inports   = num_inports
    s.sel_width     = clog2( num_inports )
    plen_width      = PLEN.stop - PLEN.start

    PLenType        = mk_bits( plen_width  )
    GrantType       = mk_bits( num_inports )
    CountType       = mk_bits( plen_width  )
    SelType         = mk_bits( s.sel_width )

    # Interface
    s.get  = [ GetIfcRTL( FlitType ) for _ in range( num_inports )  ]
    s.give = GiveIfcRTL( FlitType )

    # Components
    s.plen            = Wire( PLenType )
    s.granted_get_rdy = Wire( Bits1    )
    s.state           = Wire( Bits1    )
    s.state_next      = Wire( Bits1    )

    s.arbiter = GrantHoldArbiter( nreqs=num_inports )
    s.mux     = Mux( FlitType, num_inports )( out = s.give.msg )
    s.encoder = Encoder( num_inports, s.sel_width )(
      in_ = s.arbiter.grants,
      out = s.mux.sel,
    )
    s.counter = Counter( CountType )

    # Combinational Logic
    @s.update
    def up_granted_get_rdy():
      s.granted_get_rdy = b1(0)
      for i in range( num_inports ):
        if s.arbiter.grants[i]:
          s.granted_get_rdy = s.get[i].rdy

    for i in range( num_inports ):
      s.get[i].rdy //= s.arbiter.reqs[i]
      s.get[i].msg //= s.mux.in_[i]

    @s.update
    def up_get_en():
      for i in range( num_inports ):
        s.get[i].en = s.give.en & ( s.mux.sel == SelType(i) )

    # FIXME: use the lambda syntax after updating pymtl3 which fix the
    # transalation bug
    # for i in range( num_inports ):
    #   s.get[i].en //= lambda: s.give.en & ( s.mux.sel == SelType(i) )

    s.give.rdy           //= s.granted_get_rdy
    s.plen               //= s.mux.out[ PLEN ]
    s.counter.load_value //= s.plen
    s.counter.incr       //= b1(0) # Never increments the counter

    connect_format( s, HeaderFormat, s.mux.out )

    # State transition logic
    @s.update_ff
    def up_state():
      if s.reset:
        s.state <<= s.STATE_HEADER
      else:
        s.state <<= s.state_next

    @s.update
    def up_state_next():
      if s.state == s.STATE_HEADER:
        if s.give.en & ( s.plen > PLenType(0) ):
          s.state_next = s.STATE_BODY
        elif s.give.en & ( s.plen == PLenType(0) ):
          s.state_next = s.STATE_HEADER
        else:
          s.state_next = s.STATE_HEADER

      else: # STATE_BODY
        if ( s.counter.count == CountType(1) ) & s.give.en:
          s.state_next = s.STATE_HEADER

    # State output logic
    # TODO: counter decr
    @s.update
    def up_counter_decr():
      if s.state == s.STATE_HEADER:
        s.counter.decr = b1(0)
      else: # STATE_BODY
        s.counter.decr = s.give.en & ( s.state_next != s.STATE_HEADER )

  def line_trace( s ):
    in_trace  = '|'.join( [ str(p) for p in s.get ] )
    out_trace = f'{s.give}'
    return f'{in_trace}({s.state}){out_trace}'

