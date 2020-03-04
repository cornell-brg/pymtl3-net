'''
==========================================================================
PitonRouteUnit.py
==========================================================================
Route unit for mesh that uses XY-routing and supports multi-flit packet.

Authour : Yanghui Ou
   Date : Mar 4, 2020  
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs import GetIfcRTL, GiveIfcRTL
from ocnlib.rtl import Counter, GrantHoldArbiter
from ocnlib.utils import get_nbits, get_plen_type
from ocnlib.utils.connects import connect_bitstruct

from .directions import *
from .PitonNocHeader import PitonNocHeader

class PitonRouteUnit( Component ):

  #-----------------------------------------------------------------------
  # construct
  #-----------------------------------------------------------------------

  def construct( s, PositionType, ncols, nrows, plen_field_name='plen' ):

    # Local parameter

    assert get_nbits( PitonNocHeader ) == 64
    s.num_outports = 5
    s.PhitType     = Bits64
    s.STATE_HEADER = b1(0)
    s.STATE_BODY   = b1(1)

    PLenType = Bits8

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

    s.offchip     = Wire( Bits1 )
    s.dst_x       = Wire( Bits8 )
    s.dst_y       = Wire( Bits8 )

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

    s.offchip //= s.header.chipid[13]

    @s.update
    def up_dst():
      if s.offchip:
        s.dst_x = b8(0)
        s.dst_y = b8(nrows-1)
      else:
        s.dst_x = s.header.xpos
        s.dst_y = s.header.ypos

    @s.update
    def up_out_dir():
      if ( s.state == s.STATE_HEADER ) & s.get.rdy:
        # Offchip port
        if ( s.pos.pos_x == b8(0) ) & ( s.pos.pos_y == b8(nrows-1) ) & s.offchip:
          s.out_dir = b3( WEST )

        elif ( s.dst_x == s.pos.pos_x ) & ( s.dst_y == s.pos.pos_y ):
          s.out_dir = b3( SELF )
        elif s.dst_x < s.pos.pos_x:
          s.out_dir = b3( WEST )
        elif s.dst_x > s.pos.pos_x:
          s.out_dir = b3( EAST )
        elif s.dst_x < s.pos.pos_y:
          s.out_dir = b3( SOUTH )
        else:
          s.out_dir = b3( NORTH )
       
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
