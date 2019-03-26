#=========================================================================
# DORRouteUnitGetGiveRTL.py
#=========================================================================
# A DOR route unit with get/give interface.
#
# Author : Yanghui Ou, Cheng Tan
#   Date : Mar 25, 2019

from pymtl import *
from ocn_pclib.ifcs import GetIfcRTL, GiveIfcRTL

class DORRouteUnitGetGiveRTL( ComponentLevel6 ):

  def construct( s, PacketType, PositionType ):

    # Constants 

    s.num_outports = 5
    # TODO: define thses constants else where?
    NORTH = 0
    SOUTH = 1
    WEST  = 2
    EAST  = 3
    SELF  = 4

    # Interface

    s.recv  = GetIfcRTL( PacketType )
    s.send  = [ GiveIfcRTL (PacketType) for _ in range ( s.num_outports ) ]
    s.pos   = InVPort( PositionType )

    # Componets

    s.out_dir  = Wire( mk_bits( clog2( s.num_outports ) ) )
    s.send_ens = Wire( mk_bits( s.num_outports ) ) 

    # Connections

    for i in range( s.num_outports ):
      s.connect( s.recv.msg,    s.send[i].msg )
      s.connect( s.send_ens[i], s.send[i].en  )
    
    # Routing logic
    # TODO: implement x-dor
    @s.update
    def up_ru_routing():

      s.out_dir = 0
      for i in range( s.num_outports ):
        s.send[i].rdy = 0

      if s.recv.rdy:
        if s.pos.pos_x == s.recv.msg.dst_x and s.pos.pos_y == s.recv.msg.dst_y:
          s.out_dir = SELF
        elif s.recv.msg.dst_y < s.pos.pos_y:
          s.out_dir = NORTH
        elif s.recv.msg.dst_y > s.pos.pos_y:
          s.out_dir = SOUTH
        elif s.recv.msg.dst_x < s.pos.pos_x:
          s.out_dir = WEST
        else:
          s.out_dir = EAST
        s.send[ s.out_dir ].rdy = 1

    @s.update
    def up_ru_send_en():
      s.recv.en = s.send_ens > 0 

  # Line trace
  def line_trace( s ):

    out_str = [ "" for _ in range( s.num_outports ) ]
    for i in range (s.num_outports):
      out_str[i] = "{}".format( s.send[i] ) 

    return "{}({}){}".format( s.recv, s.out_dir, "|".join( out_str ) )
