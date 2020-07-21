'''
==========================================================================
MeshRouteUnitRTLMflitXY.py
==========================================================================
Route unit for mesh that uses XY-routing and supports multi-flit packet.

- NOTE:

It requires no tail flit and that the header flit should have a field that
indicates the length of the payload in terms of number of flits.

Authour : Yanghui Ou
   Date : Feb 9, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs import GetIfcRTL, GiveIfcRTL
from ocnlib.rtl import Counter, GrantHoldArbiter
from ocnlib.utils import get_plen_type
from ocnlib.utils.connects import connect_bitstruct
from .directions import *

class MeshRouteUnitRTLMflitXY( Component ):

  #-----------------------------------------------------------------------
  # construct
  #-----------------------------------------------------------------------

  def construct( s, HeaderFormat, PositionType, plen_field_name='plen' ):
    # Meta data
    s.num_outports = 5
    s.HeaderFormat = HeaderFormat
    s.PhitType     = mk_bits( HeaderFormat.nbits )
    s.STATE_HEADER = b1(0)
    s.STATE_BODY   = b1(1)

    PLenType = get_plen_type( HeaderFormat )

    # Interface
    s.get  = GetIfcRTL( s.PhitType )
    s.pos  = InPort( PositionType ) # TODO: figure out a way to encode position

    s.give = [ GiveIfcRTL( s.PhitType ) for _ in range( s.num_outports ) ]
    s.hold = [ OutPort( Bits1 ) for _ in range( s.num_outports ) ]

    # Components
    s.header      = Wire( HeaderFormat )
    s.state       = Wire( Bits1 )
    s.state_next  = Wire( Bits1 )
    s.out_dir_r   = Wire( Bits3 )
    s.out_dir     = Wire( Bits3 )
    s.any_give_en = Wire( Bits1 )

    s.counter = m = Counter( PLenType )
    m.incr //= 0
    m.load_value //= s.header.plen

    @update
    def up_get_ret():
      s.header @= s.get.ret

    for i in range( 5 ):
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
      if s.state == s.STATE_HEADER:
        # If the packet has body flits
        if s.any_give_en & ( s.header.plen > 0 ):
          s.state_next @= s.STATE_BODY

        else:
          s.state_next @= s.STATE_HEADER

      else: # STATE_BODY
        if ( s.counter.count == 1 ) & s.any_give_en:
          s.state_next @= s.STATE_HEADER
        else:
          s.state_next @= s.STATE_BODY

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
        if ( s.header.dst_x == s.pos.pos_x ) & ( s.header.dst_y == s.pos.pos_y ):
          s.out_dir @= SELF
        elif s.header.dst_x < s.pos.pos_x:
          s.out_dir @= WEST
        elif s.header.dst_x > s.pos.pos_x:
          s.out_dir @= EAST
        elif s.header.dst_y < s.pos.pos_y:
          s.out_dir @= SOUTH
        else:
          s.out_dir @= NORTH

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
    pos   = f'<{s.pos.pos_x},{s.pos.pos_y}>'
    count = f'{s.counter.count}'
    state = 'H' if s.state == s.STATE_HEADER else \
            'B' if s.state == s.STATE_BODY else   \
            '!'
    dir   = 'n' if s.out_dir == NORTH else \
            's' if s.out_dir == SOUTH else \
            'w' if s.out_dir == WEST  else \
            'e' if s.out_dir == EAST  else \
            'S' if s.out_dir == SELF  else \
            '?'
    return f'{s.get}({pos}[{state}{count}]{dir}{hold}){give_trace}'
