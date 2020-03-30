'''
==========================================================================
XbarRouteUnitMflitRTL.py
==========================================================================
Route unit for crossbar that supports multi-flit packet.

- NOTE:

It requires no tail flit and that the header flit should have a field that
indicates the length of the payload in terms of number of flits.

Authour : Yanghui Ou
   Date : Feb 18, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs import GetIfcRTL, GiveIfcRTL
from ocnlib.rtl import Counter, GrantHoldArbiter
from ocnlib.utils import get_plen_type
from ocnlib.utils.connects import connect_bitstruct

class XbarRouteUnitMflitRTL( Component ):

  #-----------------------------------------------------------------------
  # construct
  #-----------------------------------------------------------------------

  def construct( s, HeaderFormat, num_outports=4, plen_field_name='plen' ):
    # Meta data
    s.num_outports = num_outports
    s.HeaderFormat = HeaderFormat
    s.PhitType     = mk_bits( HeaderFormat.nbits )
    dir_nbits      = clog2( num_outports ) if num_outports > 1 else 1
    DirType        = mk_bits( dir_nbits )
    PLenType       = get_plen_type( HeaderFormat )
    s.STATE_HEADER = b1(0)
    s.STATE_BODY   = b1(1)

    # Interface
    s.get  = GetIfcRTL( s.PhitType )

    s.give = [ GiveIfcRTL( s.PhitType ) for _ in range( s.num_outports ) ]
    s.hold = [ OutPort( Bits1 ) for _ in range( s.num_outports ) ]

    # Components
    s.header      = Wire( HeaderFormat )
    s.state       = Wire()
    s.state_next  = Wire()
    s.out_dir_r   = Wire( dir_nbits )
    s.out_dir     = Wire( dir_nbits )
    s.any_give_en = Wire()

    s.counter = Counter( PLenType )
    s.counter.incr //= 0
    s.counter.load_value //= s.header.plen

    @update
    def up_header():
      s.header @= s.get.ret

    for i in range( s.num_outports ):
      s.get.ret //= s.give[i].ret
    s.get.en //= s.any_give_en

    @update
    def up_any_give_en():
      s.any_give_en @= 0
      for i in range( s.num_outports ):
        if s.give[i].en:
          s.any_give_en @= 1

    # State transition logic
    @update_ff
    def up_state_r():
      if s.reset:
        s.state <<= s.STATE_HEADER
      else:
        s.state <<= s.state_next

    @update
    def up_state_next():
      s.state_next @= s.state
      if s.state == s.STATE_HEADER:
        # If the packet has body flits
        if s.any_give_en & ( s.header.plen > 0 ):
          s.state_next @= s.STATE_BODY

      else: # STATE_BODY
        if ( s.counter.count == 1 ) & s.any_give_en:
          s.state_next @= s.STATE_HEADER

    # State output logic
    @update
    def up_counter_decr():
      if s.state == s.STATE_HEADER:
        s.counter.decr @= 0
      else:
        s.counter.decr @= s.any_give_en

    @update
    def up_counter_load():
      if s.state == s.STATE_HEADER:
        s.counter.load @= ( s.state_next == s.STATE_BODY )
      else:
        s.counter.load @= 0

    # Routing logic
    # TODO: Figure out how to encode dest id
    @update
    def up_out_dir():
      if ( s.state == s.STATE_HEADER ) & s.get.rdy:
        s.out_dir @= s.header.dst[0:dir_nbits]
      else:
        s.out_dir @= s.out_dir_r

    @update_ff
    def up_out_dir_r():
      s.out_dir_r <<= s.out_dir

    @update
    def up_give_rdy_hold():
      for i in range( s.num_outports ):
        s.give[i].rdy @= ( i == s.out_dir ) & s.get.rdy
        s.hold[i]     @= ( i == s.out_dir ) & ( s.state == s.STATE_BODY )

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    give_trace = '|'.join([ f'{ifc}' for ifc in s.give ])
    hold  = ''.join([ '^' if h else '.' for h in s.hold ])
    count = f'{s.counter.count}'
    state = 'H' if s.state == s.STATE_HEADER else \
            'B' if s.state == s.STATE_BODY else   \
            '!'
    dir   = f'{s.out_dir}'
    return f'{s.get}([{state}{count}]{dir}{hold}){give_trace}'
