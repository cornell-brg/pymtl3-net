"""
==========================================================================
PitonRouter.py
==========================================================================
Functional level piton router. 

Author : Yanghui Ou
  Date : Mar 5, 2020
"""
from pymtl3 import *
from ocnlib.utils import to_bitstruct

from .directions import *
from .PitonNoCHeader import PitonNoCHeader

#-------------------------------------------------------------------------
# MeshRouterMflitFL
#-------------------------------------------------------------------------
# Mesh router that supports single flit packet.

class PitonRouterFL:

  def __init__( s, pos_x, pos_y, first_dimension='x' ):
    s.pos_x           = pos_x
    s.pos_y           = pos_y
    s.first_dimension = first_dimension

  def arrange_src_pkts( s, lst ):
    src_pkts = [ [] for _ in range(5) ]
    if s.first_dimension == 'y':
      for pkt in lst:
        src_x = 0 if pkt.src_offchip else pkt.src_x
        src_y = 0 if pkt.src_offchip else pkt.src_y
        if pkt.src_offchip and s.pos_x == 0 and s.pos_y == 0:
          src_pkts[ WEST ].append( pkt )
        elif src_x == s.pos_x and src_y == s.pos_y:
          src_pkts[ SELF ].append( pkt )
        elif src_x == s.pos_x:
          if src_y < s.pos_y:
            src_pkts[ NORTH ].append( pkt )
          else:
            src_pkts[ SOUTH ].append( pkt )
        elif src_x < s.pos_x:
          src_pkts[ WEST ].append( pkt )
        else:
          src_pkts[ EAST ].append( pkt )

    elif s.first_dimension == 'x':
      for pkt in lst:
        src_x = 0 if pkt.src_offchip else pkt.src_x
        src_y = 0 if pkt.src_offchip else pkt.src_y
        if pkt.src_offchip and s.pos_x == 0 and s.pos_y == 0:
          src_pkts[ WEST ].append( pkt )
        if src_x == s.pos_x and src_y == s.pos_y:
          src_pkts[ SELF ].append( pkt )
        elif src_y == s.pos_y:
          if src_x < s.pos_x:
            src_pkts[ WEST ].append( pkt )
          else:
            src_pkts[ SOUTH ].append( pkt )
        elif src_y < s.pos_y:
          src_pkts[ NORTH ].append( pkt )
        else:
          src_pkts[ SOUTH ].append( pkt )
    else:
      assert False

    return src_pkts

  def route( s, src_pkts ):
    assert len( src_pkts ) == 5
    dst_pkts = [ [] for _ in range(5) ]

    if s.first_dimension == 'y':
      for pkts in src_pkts:
        for pkt in pkts:
          header = to_bitstruct( pkt.flits[0], PitonNoCHeader )
          dst_x = 0 if header.chipid[13] else header.xpos
          dst_y = 0 if header.chipid[13] else header.ypos
          dst = (
            WEST  if header.chipid[13] and s.pos_x == 0 and s.pos_y == 0 else
            SELF  if dst_x == s.pos_x and dst_y == s.pos_y else
            SOUTH if dst_y > s.pos_y else
            NORTH if dst_y < s.pos_y else
            EAST  if dst_x > s.pos_x else
            WEST
          )
          dst_pkts[ dst ].append( pkt )

    elif s.first_dimension == 'x':
      for pkts in src_pkts:
        for pkt in pkts:
          header = to_bitstruct( pkt.flits[0], PitonNoCHeader )
          dst_x = 0 if header.chipid[13] else header.xpos
          dst_y = 0 if header.chipid[13] else header.ypos
          dst = (
            WEST  if header.chipid[13] and s.pos_x == 0 and s.pos_y == 0 else
            SELF  if dst_x == s.pos_x and dst_y == s.pos_y else
            EAST  if dst_x > s.pos_x else
            WEST  if dst_x < s.pos_x else
            SOUTH if dst_y > s.pos_y else
            NORTH 
          )
          dst_pkts[ dst ].append( pkt )

    else:
      assert False

    return dst_pkts
