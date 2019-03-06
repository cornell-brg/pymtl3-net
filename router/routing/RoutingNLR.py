#=========================================================================
# RoutingNLR.py
#=========================================================================
# A north last routing (NLR) strategy initial implementation
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 3, 2019

from pymtl  import *
from ocn_pclib.Packet import Packet

class RoutingNLR( RTLComponent ):
  def construct( s, PktType, addr_wid=Bits4 ):
    
    # Interface
    s.pkt_in  = InVPort( PktType  )
    s.pos_x   = InVPort( addr_wid )
    s.pos_y   = InVPort( addr_wid )
    s.out_dir = OutVPort( Bits3 )

    # Constants
    s.NORTH = 0
    s.SOUTH = 1
    s.WEST  = 2
    s.EAST  = 3
    s.SELF  = 4

    @s.update
    def process():

      s.out_dir = 0

      if s.pos_x == s.pkt_in.dst_x and s.pos_y == s.pkt_in.dst_y:
        s.out_dir = s.SELF
      elif s.pkt_in.dst_x < s.pos_x:
        s.out_dir = s.WEST
      elif s.pkt_in.dst_x > s.pos_x:
        s.out_dir = s.EAST
      elif s.pkt_in.dst_y > s.pos_y:
        s.out_dir = s.SOUTH
      else:
        s.out_dir = s.NORTH

