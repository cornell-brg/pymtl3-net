#=========================================================================
# DORYCMeshFlitRouteUnitRTL.py
#=========================================================================
# A DOR-Y route unit supporting flit for CMesh.
#
# Author : Cheng Tan, Yanghui Ou
#   Date : July 13, 2019

from pymtl3     import *
from directions import *
from pymtl3.stdlib.ifcs import GetIfcRTL, GiveIfcRTL

class DORYCMeshFlitRouteUnitRTL( Component ):

  def construct( s, MsgType, PositionType, num_outports = 5 ):

    # Constants 

    s.num_outports = num_outports
    TType = mk_bits( num_outports )

    # Interface

    s.get     = GetIfcRTL( MsgType )
    s.give    = [ GiveIfcRTL (MsgType) for _ in range ( s.num_outports ) ]
    s.pos     = InPort( PositionType )
    s.out_ocp = [ InPort( Bits1 ) for _ in range( s.num_outports ) ]

    # Componets

    s.out_dir  = Wire( mk_bits( clog2( s.num_outports ) ) )
    s.give_ens = Wire( mk_bits( s.num_outports ) ) 
    s.give_rdy = [ Wire( Bits1 ) for _ in range( s.num_outports ) ]

    # Connections

    for i in range( s.num_outports ):
      s.connect( s.get.msg,     s.give[i].msg )
      s.connect( s.give_ens[i], s.give[i].en  )
      s.connect( s.give_rdy[i], s.give[i].rdy )
    
    # Routing logic
    @s.update
    def up_ru_routing():
 
      for i in range( s.num_outports ):
        s.give_rdy[i] = Bits1(0)

      if s.get.rdy:
        if s.get.msg.fl_type == 0:
          if s.pos.pos_x == s.get.msg.dst_x and s.pos.pos_y == s.get.msg.dst_y:
            if s.out_ocp[4] == 0:
              s.give_rdy[Bits3(4)+s.get.msg.dst_ter] = Bits1(1)
              s.out_dir = 4 + s.get.msg.dst_ter
          elif s.get.msg.dst_y < s.pos.pos_y:
            if s.out_ocp[1] == 0:
              s.give_rdy[1] = Bits1(1)
              s.out_dir = 1
          elif s.get.msg.dst_y > s.pos.pos_y:
            if s.out_ocp[0] == 0:
              s.give_rdy[0] = Bits1(1)
              s.out_dir = 0
          elif s.get.msg.dst_x < s.pos.pos_x:
            if s.out_ocp[2] == 0:
              s.give_rdy[2] = Bits1(1)
              s.out_dir = 2
          else:
            if s.out_ocp[3] == 0:
              s.give_rdy[3] = Bits1(1)
              s.out_dir = 3
        else:
          s.give_rdy[s.out_dir] = Bits1(1)

    @s.update
    def up_ru_get_en():
      s.get.en = s.give_ens > TType(0) 

  # Line trace
  def line_trace( s ):
    out_str = [ "" for _ in range( s.num_outports ) ]
    for i in range (s.num_outports):
      out_str[i] = "{}".format( s.give[i] ) 
    return "{}{}".format( s.get, "|".join( out_str ) )
