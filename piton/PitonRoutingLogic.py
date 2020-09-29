'''
==========================================================================
PitonRoutingLogic.py
==========================================================================
Combinational routing logic that computes the destinattion based on the
position and destination.

Author : Yanghui Ou
  Date : Sep 26, 2020
'''
from pymtl3 import *

from .directions import *
from .PitonNoCHeader import PitonNoCHeader

FBITS_WEST  = 0b0010
FBITS_SOUTH = 0b0011
FBITS_EAST  = 0b0100
FBITS_NORTH = 0b0101
FBITS_PROC  = 0b0000

class PitonRoutingLogic( Component ):

  def construct( s, PositonType ):

    # Interface

    s.in_header = InPort( PitonNoCHeader )
    s.in_pos    = InPort( PositonType )
    s.out_dir   = OutPort( Bits3 )

    # Wires

    s.offchip = Wire( Bits1 )
    s.dst_x   = Wire( Bits8 )
    s.dst_y   = Wire( Bits8 )

    # Routing logic

    s.offchip //= lambda: s.in_header.chipid != s.in_pos.chipid

    @update
    def up_dst():
      s.dst_x @= 0
      s.dst_y @= 0
      if ~s.offchip:
        s.dst_x @= s.in_header.xpos
        s.dst_y @= s.in_header.ypos

    @update
    def up_out_dir():
      s.out_dir @= 0

      # Offchip port
      if ( s.in_pos.pos_x == 0 ) & ( s.in_pos.pos_y == 0 ) & s.offchip:
        s.out_dir @= NORTH

      elif ( s.dst_x == s.in_pos.pos_x ) & ( s.dst_y == s.in_pos.pos_y ):
        # Use fbits to route to final destination
        if s.in_header.fbits == FBITS_NORTH:
          s.out_dir @= NORTH
        elif s.in_header.fbits == FBITS_SOUTH:
          s.out_dir @= SOUTH
        elif s.in_header.fbits == FBITS_WEST:
          s.out_dir @= WEST
        elif s.in_header.fbits == FBITS_EAST:
          s.out_dir @= EAST
        else:
          s.out_dir @= SELF

      elif s.dst_x < s.in_pos.pos_x:
        s.out_dir @= WEST
      elif s.dst_x > s.in_pos.pos_x:
        s.out_dir @= EAST
      elif s.dst_y < s.in_pos.pos_y:
        s.out_dir @= NORTH
      else: # s.dst_y > s.pos.pos_y:
        s.out_dir @= SOUTH

  def line_trace( s ):
    return f''

