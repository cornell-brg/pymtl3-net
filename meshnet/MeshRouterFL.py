"""
==========================================================================
MeshRouteFL.py
==========================================================================
Functional level implementation of mesh router.

Author : Yanghui Ou
  Date : July 3, 2019
"""
from pymtl3 import *
from ocnlib.utils import to_bitstruct

from .directions import *


#-------------------------------------------------------------------------
# MeshRouterFL
#-------------------------------------------------------------------------
# Mesh router that supports single flit packet.

class MeshRouterFL:

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

#-------------------------------------------------------------------------
# MeshRouterFL
#-------------------------------------------------------------------------
# Mesh router that supports single flit packet.

class MeshRouterMFlitFL:

  def __init__( s, Header, pos_x, pos_y, first_dimension='x' ):
    s.Header          = Header
    s.pos_x           = pos_x
    s.pos_y           = pos_y
    s.first_dimension = first_dimension

  def arrange_src_pkts( s, lst ):
    src_pkts = [ [] for _ in range(5) ]
    if s.first_dimension == 'y':
      for pkt in lst:
        header = to_bitstruct( pkt.flits[0], s.Header )
        if header.src_x == s.pos_x and header.src_y == s.pos_y:
          src_pkts[ SELF ].append( pkt )
        elif header.src_x == s.pos_x:
          if header.src_y < s.pos_y:
            src_pkts[ SOUTH ].append( pkt )
          else:
            src_pkts[ NORTH ].append( pkt )
        elif header.src_x < s.pos_x:
          src_pkts[ WEST ].append( pkt )
        else:
          src_pkts[ EAST ].append( pkt )

    elif s.first_dimension == 'x':
      for pkt in lst:
        header = to_bitstruct( pkt.flits[0], s.Header )
        if header.src_x == s.pos_x and header.src_y == s.pos_y:
          src_pkts[ SELF ].append( pkt )
        elif header.src_y == s.pos_y:
          if header.src_x < s.pos_x:
            src_pkts[ WEST ].append( pkt )
          else:
            src_pkts[ NORTH ].append( pkt )
        elif header.src_y < s.pos_y:
          src_pkts[ SOUTH ].append( pkt )
        else:
          src_pkts[ NORTH ].append( pkt )
    else:
      assert False

    return src_pkts

  def route( s, src_pkts ):
    assert len( src_pkts ) == 5
    dst_pkts = [ [] for _ in range(5) ]

    if s.first_dimension == 'y':
      for pkts in src_pkts:
        for pkt in pkts:
          header = to_bitstruct( pkt.flits[0], s.Header )
          dst = (
            SELF  if header.dst_x == s.pos_x and pkt.dst_y == s.pos_y else
            NORTH if header.dst_y > s.pos_y else
            SOUTH if header.dst_y < s.pos_y else
            EAST  if header.dst_x > s.pos_x else
            WEST
          )
          dst_pkts[ dst ].append( pkt )

    elif s.first_dimension == 'x':
      for pkts in src_pkts:
        for pkt in pkts:
          header = to_bitstruct( pkt.flits[0], s.Header )
          dst = (
            SELF  if header.dst_x == s.pos_x and pkt.dst_y == s.pos_y else
            EAST  if header.dst_x > s.pos_x else
            WEST  if header.dst_x < s.pos_x else
            NORTH if header.dst_y > s.pos_y else
            SOUTH
          )
          dst_pkts[ dst ].append( pkt )

    else:
      assert False

    return dst_pkts
