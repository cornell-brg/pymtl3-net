"""
==========================================================================
MeshRouteFL.py
==========================================================================
Functional level implementation of mesh router.

Author : Yanghui Ou
  Date : July 3, 2019
"""
from pymtl3 import *
from directions import *

class MeshRouterFL( object ):

  def __init__( s, pos_x, pos_y, dimension='y' ):
    s.pos_x = pos_x
    s.pos_y = pos_y
    s.dimension = dimension

  def arrange_src_pkts( s, lst ):
    src_pkts = [ [] for _ in range(5) ]
    if s.dimension == 'y':
      for pkt in lst:
        if pkt.src_x == s.pos_x and pkt.src_y == s.pos_y:
          src_pkts[SELF].append( pkt )
        elif pkt.src_x == s.pos_x:
          if pkt.src_y < s.pos_y:
            src_pkts[SOUTH].append( pkt )
          else:
            src_pkts[NORTH].append( pkt )
        elif pkt.src_x < s.pos_x:
          src_pkts[WEST].append( pkt )
        else:
          src_pkts[EAST].append( pkt )

    else: # s.dimension == 'x'
      for pkt in lst:
        if pkt.src_x == s.pos_x and pkt.src_y == s.pos_y:
          src_pkts[SELF].append( pkt )
        elif pkt.src_y == s.pos_y:
          if pkt.src_x < s.pos_x:
            src_pkts[WEST].append( pkt )
          else:
            src_pkts[NORTH].append( pkt )
        elif pkt.src_y < s.pos_y:
          src_pkts[SOUTH].append( pkt )
        else:
          src_pkts[NORTH].append( pkt )

    return src_pkts

  def route( s, src_pkts ):
    assert len( src_pkts ) == 5
    dst_pkts = [ [] for _ in range(5) ]

    if s.dimension == 'y':
      for pkts in src_pkts:
        for pkt in pkts:
          dst = (
            SELF  if pkt.dst_x == s.pos_x and pkt.dst_y == s.pos_y else
            NORTH if pkt.dst_y > s.pos_y else
            SOUTH if pkt.dst_y < s.pos_y else
            EAST  if pkt.dst_x > s.pos_x else
            WEST
          )
          dst_pkts[ dst ].append( pkt )

    else: # s.dimension == 'x'
      for pkts in src_pkts:
        for pkt in pkts:
          dst = (
            SELF  if pkt.dst_x == s.pos_x and pkt.dst_y == s.pos_y else
            EAST  if pkt.dst_x > s.pos_x else
            WEST  if pkt.dst_x < s.pos_x else
            NORTH if pkt.dst_y > s.pos_y else
            SOUTH
          )
          dst_pkts[ dst ].append( pkt )

    return dst_pkts