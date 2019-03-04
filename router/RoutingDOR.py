#=========================================================================
# RoutingDOR.py
#=========================================================================
# A dimension-order routing (DOR) strategy initial implementation
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 3, 2019

from pymtl  import *
from Packet import Packet

class RoutingDOR( RTLComponent ):
  dimension = 'x'
  NORTH = 0
  SOUTH = 1
  WEST  = 2
  EAST  = 3
  SELF  = 4
  def construct( s, dimension ):
    s.dimension = dimension

  def set_dimension ( s, dimension ):
    s.dimension = dimension

  def compute_output( s, pos_x, pos_y, pkt = Packet):

    out_dir = 0

    if s.dimension == 'x':
      if pos_x == pkt.dst_x and pos_y == pkt.dst_y:
        out_dir = s.SELF
      elif pkt.dst_x < pos_x:
        out_dir = s.WEST
      elif pkt.dst_x > pos_x:
        out_dir = s.EAST
      elif pkt.dst_y < pos_y:
        out_dir = s.NORTH
      else:
        out_dir = s.SOUTH
  
    elif s.dimension == 'y':
      if pos_x == pkt.dst_x and pos_y == pkt.dst_y:
        out_dir = s.SELF
      elif pkt.dst_y < pos_y:
        out_dir = s.NORTH
      elif pkt.dst_y > pos_y:
        out_dir = s.SOUTH
      elif pkt.dst_x < pos_x:
        out_dir = s.WEST
      else:
        out_dir = s.EAST

    else:
      raise AssertionError( "Invalid input for dimension: %s " % dimension )

    return out_dir
