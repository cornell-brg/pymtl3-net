#=========================================================================
# RoutingDOR.py
#=========================================================================
# A dimension-order routing (DOR) strategy initial implementation
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 3, 2019

from pymtl  import *
from ocn_pclib.Packet   import Packet
from ocn_pclib.Position import *

class RoutingDORX( RTLComponent ):
  def construct( s, PktType, addr_wid=Bits4 ):
    
    # Interface

    s.pkt_in  = InVPort( PktType  )
    s.pos     = InVPort ( MeshPosition )
    s.out_dir = OutVPort( Bits3 )
    
    # Constants

    s.NORTH = 0
    s.SOUTH = 1
    s.WEST  = 2
    s.EAST  = 3
    s.SELF  = 4

#    print s.pkt_in
    @s.update
    def process():
      s.out_dir = 0
      if s.pos.pos_x == s.pkt_in.dst_x and s.pos.pos_y == s.pkt_in.dst_y:
        s.out_dir = s.SELF
      elif s.pkt_in.dst_x < s.pos.pos_x:
        s.out_dir = s.WEST
      elif s.pkt_in.dst_x > s.pos.pos_x:
        s.out_dir = s.EAST
      elif s.pkt_in.dst_y < s.pos.pos_y:
        s.out_dir = s.NORTH
      else:
        s.out_dir = s.SOUTH
    
#      else:
#        raise AssertionError( "Invalid input for dimension: %s " % dimension )

#  def set_dimension ( s, dimension ):
#    s.dimension = dimension

#  def compute_output( s, s.pos.pos_x, s.pos.pos_y, s.pkt_in = Packet):
