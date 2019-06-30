"""
==========================================================================
TorusRouterFL.py
==========================================================================
FL route unit that implements dimension order routing.

Author : Yanghui Ou
  Date : June 30, 2019
"""
from pymtl3 import *
from directions import *

from .RouteUnitDorFL import RouteUnitDorFL

class TorusRouterFL( object ):

  def __init__( s, pos_x, pos_y, ncols, nrows, dimension='y' ):
    s.route_unit = RouteUnitDorFL( pos_x, pos_y, ncols, nrows, dimension='y' )

  def route( s, src_pkts ):
    assert len( src_pkts ) == 5

    dst_pkts = [ [] for _ in range(5) ]

    for pkts in src_pkts:
      tmp = s.route_unit.route( pkts )
      for i in range(5):
        dst_pkts[i].extend( tmp[i] )

    return dst_pkts