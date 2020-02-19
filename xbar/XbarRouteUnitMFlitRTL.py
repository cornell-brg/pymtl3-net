'''
==========================================================================
XbarRouteUnitMFlitRTL.py
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
from ocnlib.utils import get_nbits, get_plen_type
from ocnlib.utils.connects import connect_bitstruct
from .directions import *

class XbarRouteUnitMFlitRTL( Component ):

  #-----------------------------------------------------------------------
  # construct
  #-----------------------------------------------------------------------

  def construct( s, HeaderFormat, num_outports=4, plen_field_name='plen' ):
    # Meta data
    s.num_outports = num_outports
    s.HeaderFormat = HeaderFormat
    s.PhitType     = mk_bits( get_nbits( HeaderFormat ) )
    s.STATE_HEADER = b1(0)
    s.STATE_BODY   = b1(1)

    PLenType = get_plen_type( HeaderFormat )

    # Interface
    s.get  = GetIfcRTL( s.PhitType )

    s.give = [ GiveIfcRTL( s.PhitType ) for _ in range( s.num_outports ) ]
    s.hold = [ OutPort( Bits1 ) for _ in range( s.num_outports ) ]

    # Components
    s.header      = Wire( HeaderFormat )
    s.state       = Wire( Bits1 )
    s.state_next  = Wire( Bits1 )
    s.out_dir_r   = Wire( Bits3 )
    s.out_dir     = Wire( Bits3 )
    s.any_give_en = Wire( Bits1 )

    s.counter = Counter( PLenType )(
      incr=b1(0),
      load_value=s.header.plen,
    )

    connect_bitstruct( s.get.ret, s.header )
    
    for i in range( 5 ):
      s.get.ret //= s.give[i].ret
    s.get.en //= s.any_give_en

    @s.update
    def up_any_give_en():
      s.any_give_en = b1(0)
      for i in range( s.num_outports ):
        if s.give[i].en:
          s.any_give_en = b1(1)

    # State transition logic
    @s.update_ff
    def up_state_r():
      if s.reset:
        s.state <<= s.STATE_HEADER
      else:
        s.state <<= s.state_next

    @s.update
    def up_state_next():
      if s.state == s.STATE_HEADER:
        # If the packet has body flits
        if s.any_give_en & ( s.header.plen > PLenType(0) ):
          s.state_next = s.STATE_BODY

        else:
          s.state_next = s.STATE_HEADER

      else: # STATE_BODY
        if ( s.counter.count == PLenType(1) ) & s.any_give_en:
          s.state_next = s.STATE_HEADER

    # State output logic
    @s.update
    def up_counter_decr():
      if s.state == s.STATE_HEADER:
        s.counter.decr = b1(0)
      else:
        s.counter.decr = s.any_give_en

    @s.update
    def up_counter_load():
      if s.state == s.STATE_HEADER:
        s.counter.load = ( s.state_next == s.STATE_BODY )
      else:
        s.counter.load = b1(0)


    # Routing logic
    # TODO: Figure out how to encode dest id
    @s.update
    def up_out_dir():
      if ( s.state == s.STATE_HEADER ) & s.get.rdy:
        s.out_dir = s.get.ret.dst
       
      else:
        s.out_dir = s.out_dir_r

    @s.update_ff
    def up_out_dir_r():
      s.out_dir_r <<= s.out_dir

    @s.update
    def up_give_rdy_hold():
      for i in range( s.num_outports ):
        s.give[i].rdy = ( b3(i) == s.out_dir ) & s.get.rdy
        s.hold[i]     = ( b3(i) == s.out_dir ) & ( s.state == s.STATE_BODY )

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
    dir   = f's.out_dir'
    return f'{s.get}([{state}{count}]{dir}{hold}){give_trace}'
