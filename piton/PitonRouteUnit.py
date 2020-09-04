'''
==========================================================================
PitonRouteUnit.py
==========================================================================
Route unit for mesh that uses XY-routing and supports multi-flit packet.

NOTE - OpenPiton's coordinate system looks like this:

0 ------------------> x
 | (0, 0)  (1, 0)
 | (0, 1)  (1, 1)
 | ...
 |
 | (0, 6)  (1, 6)
 v
y

Authour : Yanghui Ou
   Date : Mar 4, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs import GetIfcRTL, GiveIfcRTL
from ocnlib.rtl import Counter, GrantHoldArbiter
from ocnlib.utils import get_field_type
from ocnlib.utils.connects import connect_bitstruct

from .directions import *
from .PitonNoCHeader import PitonNoCHeader

FBITS_WEST  = 0b0010
FBITS_SOUTH = 0b0011
FBITS_EAST  = 0b0100
FBITS_NORTH = 0b0101
FBITS_PROC  = 0b0000

class PitonRouteUnit( Component ):

  #-----------------------------------------------------------------------
  # construct
  #-----------------------------------------------------------------------

  def construct( s, PositionType, plen_field_name='plen' ):

    # Local parameter

    assert PitonNoCHeader.nbits == 64
    s.num_outports = 5
    s.PhitType     = Bits64
    s.STATE_HEADER = 0
    s.STATE_BODY   = 1

    PLenType = Bits8
    XType    = get_field_type( PositionType, 'pos_x' )
    YType    = get_field_type( PositionType, 'pos_y' )

    # Interface

    s.get  = GetIfcRTL( s.PhitType )
    s.pos  = InPort( PositionType ) # TODO: figure out a way to encode position

    s.give = [ GiveIfcRTL( s.PhitType ) for _ in range( s.num_outports ) ]
    s.hold = [ OutPort( Bits1 ) for _ in range( s.num_outports ) ]

    # Components

    s.header      = Wire( PitonNoCHeader )
    s.state       = Wire( Bits1 )
    s.state_next  = Wire( Bits1 )
    s.out_dir_r   = Wire( Bits3 )
    s.out_dir     = Wire( Bits3 )
    s.any_give_en = Wire( Bits1 )

    s.offchip     = Wire( Bits1 )
    s.dst_x       = Wire( Bits8 )
    s.dst_y       = Wire( Bits8 )

    s.counter = Counter( PLenType )
    s.counter.incr //= 0
    s.counter.load_value //= s.header.plen

    connect_bitstruct( s.get.ret, s.header )

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
      s.counter.decr @= 0
      if s.state != s.STATE_HEADER:
        s.counter.decr @= s.any_give_en

    @update
    def up_counter_load():
      s.counter.load @= 0
      if s.state == s.STATE_HEADER:
        s.counter.load @= ( s.state_next == s.STATE_BODY )

    # Routing logic

    s.offchip //= lambda: s.header.chipid != s.pos.chipid

    @update
    def up_dst():
      s.dst_x @= 0
      s.dst_y @= 0
      if ~s.offchip:
        s.dst_x @= s.header.xpos
        s.dst_y @= s.header.ypos

    @update
    def up_out_dir():
      s.out_dir @= s.out_dir_r

      if ( s.state == s.STATE_HEADER ) & s.get.rdy:
        s.out_dir @= 0

        # Offchip port
        if ( s.pos.pos_x == 0 ) & ( s.pos.pos_y == 0 ) & s.offchip:
          s.out_dir @= NORTH

        elif ( s.dst_x == s.pos.pos_x ) & ( s.dst_y == s.pos.pos_y ):
          # Use fbits to route to final destination
          if s.header.fbits == FBITS_NORTH:
            s.out_dir @= NORTH
          elif s.header.fbits == FBITS_SOUTH:
            s.out_dir @= SOUTH
          elif s.header.fbits == FBITS_WEST:
            s.out_dir @= WEST
          elif s.header.fbits == FBITS_EAST:
            s.out_dir @= EAST
          else:
            s.out_dir @= SELF

        elif s.dst_x < s.pos.pos_x:
          s.out_dir @= WEST
        elif s.dst_x > s.pos.pos_x:
          s.out_dir @= EAST
        elif s.dst_y < s.pos.pos_y:
          s.out_dir @= NORTH
        else: # s.dst_y > s.pos.pos_y:
          s.out_dir @= SOUTH

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

