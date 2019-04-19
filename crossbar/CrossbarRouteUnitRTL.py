#=========================================================================
# CrossbarRouteUnitRTL.py
#=========================================================================
# A crossbar route unit with get/give interface.
#
# Author : Yanghui Ou, Cheng Tan
#   Date : April 18, 2019

from pymtl          import *
from ocn_pclib.ifcs import GetIfcRTL, GiveIfcRTL

class CrossbarRouteUnitRTL( Component ):

  def construct( s, PacketType, num_outports ):

    # Constants 
    s.num_outports = num_outports 

    # Interface

    s.get  = GetIfcRTL( PacketType )
    s.give = [ GiveIfcRTL (PacketType) for _ in range ( s.num_outports ) ]

    # Componets

    s.give_ens = Wire( mk_bits( s.num_outports ) ) 

    # Connections

    for i in range( s.num_outports ):
      s.connect( s.get.msg,     s.give[i].msg )
      s.connect( s.give_ens[i], s.give[i].en  )
    
    # Routing logic
    @s.update
    def up_ru_routing():
 
      for i in range( s.num_outports ):
        s.give[i].rdy = 0

      if s.get.rdy:
        s.give[ s.get.msg.dst ].rdy = 1

    @s.update
    def up_ru_get_en():
      s.get.en = s.give_ens > 0 

  # Line trace
  def line_trace( s ):

    out_str = [ "" for _ in range( s.num_outports ) ]
    for i in range (s.num_outports):
      out_str[i] = "{}".format( s.give[i] ) 

    return "{}({}){}".format( s.get, s.get.msg.dst, "|".join( out_str ) )
