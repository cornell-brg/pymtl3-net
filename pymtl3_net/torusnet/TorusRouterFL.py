"""
==========================================================================
TorusRouterFL.py
==========================================================================
FL route unit that implements dimension order routing.

Author : Yanghui Ou
  Date : June 30, 2019
"""
from pymtl3 import *

from .directions import *
from .RouteUnitDorFL import RouteUnitDorFL


class TorusRouterFL:

  def __init__( s, pos_x, pos_y, ncols, nrows, dimension='y' ):
    s.pos_x = pos_x
    s.pos_y = pos_y
    s.ncols = ncols
    s.nrows = nrows
    s.dimension  = dimension
    s.route_unit = RouteUnitDorFL( pos_x, pos_y, ncols, nrows, dimension='y' )

  #-----------------------------------------------------------------------
  # arrange_src_pkts
  #-----------------------------------------------------------------------
  # A helper function that puts each packet in [lst] into corresponding
  # source.

  def arrange_src_pkts( s, lst ):
    src_pkts = [ [] for _ in range(5) ]

    for pkt in lst:
      if pkt.src_x == s.pos_x and pkt.src_y == s.pos_y:
        in_dir = SELF

      elif s.dimension == 'y':
        src_x = pkt.src_x.uint()
        src_y = pkt.src_y.uint()
        dst_x = pkt.dst_x.uint()
        dst_y = pkt.dst_y.uint()

        # Same x - either comes from north or south
        if src_x == s.pos_x:
          north_dist = dst_y - src_y if dst_y > src_y else dst_y + s.nrows - src_y
          south_dist = src_y - dst_y if dst_y < src_y else src_y + s.nrows - dst_y
          in_dir = SOUTH if north_dist < south_dist else NORTH

        # Different x - either comes from west or east
        else:
          east_dist  = dst_x - src_x if dst_x > src_x else dst_x + s.ncols - src_x
          west_dist  = src_x - dst_x if dst_x < src_x else src_x + s.ncols - dst_x
          in_dir = EAST if west_dist < east_dist else WEST

      else: # s.dimension=='x'

        # Same y - either comes from west or east
        if src_x == s.pos_x:
          east_dist  = dst_x - src_x if dst_x > src_x else dst_x + s.ncols - src_x
          west_dist  = src_x - dst_x if dst_x < src_x else src_x + s.ncols - dst_x
          in_dir = EAST if west_dist < east_dist else WEST

        # Different y - either comes from north or south
        else:
          north_dist = dst_y - src_y if dst_y > src_y else dst_y + s.nrows - src_y
          south_dist = src_y - dst_y if dst_y < src_y else src_y + s.nrows - dst_y
          in_dir = SOUTH if north_dist < south_dist else NORTH

      src_pkts[ in_dir ].append( pkt )

    return src_pkts

  #-----------------------------------------------------------------------
  # route
  #-----------------------------------------------------------------------
  # Use FL route unit to route each packet in [src_pkts] to corresponding
  # destination.

  def route( s, src_pkts ):
    assert len( src_pkts ) == 5

    dst_pkts = [ [] for _ in range(5) ]

    for pkts in src_pkts:
      tmp = s.route_unit.route( pkts )
      for i in range(5):
        dst_pkts[i].extend( tmp[i] )

    return dst_pkts
