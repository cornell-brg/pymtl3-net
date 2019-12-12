"""
==========================================================================
RouteUnitDorFL.py
==========================================================================
FL route unit that implements dimension order routing.

Author : Yanghui Ou
  Date : June 30, 2019
"""
from pymtl3 import *

from .directions import *


class RouteUnitDorFL:

  def __init__( s, pos_x, pos_y, ncols, nrows, dimension='y' ):
    s.pos_x = pos_x
    s.pos_y = pos_y
    s.ncols = ncols
    s.nrows = nrows
    s.dimension   = dimension
    s.last_row_id = nrows-1
    s.last_col_id = ncols-1

  def route( s, src_pkts ):
    dst_pkts = [ [] for _ in range(5) ]

    for pkt in src_pkts:
      if pkt.dst_x == s.pos_x and pkt.dst_y == s.pos_y:
        dst_pkts[ SELF ].append( pkt )
      else:
        north_dist = pkt.dst_y - s.pos_y if pkt.dst_y > s.pos_y else pkt.dst_y + s.nrows - s.pos_y
        south_dist = s.pos_y - pkt.dst_y if pkt.dst_y < s.pos_y else s.pos_y + s.nrows - pkt.dst_y
        east_dist  = pkt.dst_x - s.pos_x if pkt.dst_x > s.pos_x else pkt.dst_x + s.ncols - s.pos_x
        west_dist  = s.pos_x - pkt.dst_x if pkt.dst_x < s.pos_x else s.pos_x + s.ncols - pkt.dst_x

        if s.dimension == 'y':
          if pkt.dst_y != s.pos_y:
            out_dir = NORTH if north_dist < south_dist else SOUTH
          else:
            out_dir = WEST if west_dist < east_dist else EAST
          dst_pkts[ out_dir ].append( pkt )

        else: # s.dimension=='x'
          if pkt.dst_x != s.pos_x:
            out_dir = WEST if west_dist < east_dist else EAST
          else:
            out_dir = NORTH if north_dist < south_dist else SOUTH
          dst_pkts[ out_dir ].append( pkt )

    return dst_pkts
