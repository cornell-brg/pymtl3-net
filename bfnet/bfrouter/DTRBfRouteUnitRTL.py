#=========================================================================
# DTRBfRouteUnitRTL.py
#=========================================================================
# A butterfly route unit with get/give interface.
#
# Author : Yanghui Ou, Cheng Tan
#   Date : April 6, 2019

from pymtl import *
from ocn_pclib.ifcs import GetIfcRTL, GiveIfcRTL

class DTRBfRouteUnitRTL( Component ):

  def construct( s, PacketType, PositionType, num_outports, n_fly = 3 ):

    # Constants 

    s.num_outports = num_outports
    k_ary = num_outports

    # Interface

    s.get  = GetIfcRTL( PacketType )
    s.give = [ GiveIfcRTL (PacketType) for _ in range ( s.num_outports ) ]
    s.pos  = InPort( PositionType )

    # Componets

    s.out_dir  = Wire( mk_bits( clog2( s.num_outports ) ) )
    s.give_ens = Wire( mk_bits( s.num_outports ) ) 

    # Connections

    for i in range( s.num_outports ):
      s.connect( s.get.msg,     s.give[i].msg )
      s.connect( s.give_ens[i], s.give[i].en  )
    
    # Routing logic
    @s.update
    def up_ru_routing():
 
      s.out_dir = 0
      for i in range( s.num_outports ):
        s.give[i].rdy = 0

      if s.get.rdy:
        # TODO: or embed this into the pos/packet
#        mod = k_ary**(n_fly-((int)(s.pos.pos))/(k_ary**(n_fly-1)))
#        div = k_ary**(n_fly-((int)(s.pos.pos))/(k_ary**(n_fly-1))-1)
#        s.out_dir = ((int)(s.get.msg.dst_x) % mod) / div
        print s.get.msg
        s.out_dir = s.get.msg.dst[ s.pos.stage ]
        s.give[ s.out_dir ].rdy = 1

    @s.update
    def up_ru_get_en():
      s.get.en = s.give_ens > 0 

  # Line trace
  def line_trace( s ):

    out_str = [ "" for _ in range( s.num_outports ) ]
    for i in range (s.num_outports):
      out_str[i] = "{}".format( s.give[i] ) 

    return "{}({}){}".format( s.get, s.out_dir, "|".join( out_str ) )
