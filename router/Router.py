#=========================================================================
# Router.py
#=========================================================================
# Network-on-chip router (basic class)
# could be inherented by FL, CL, and RTL
#
# Author : Cheng Tan
#   Date : Mar 21 2019

class Router:
  def __construct__( s, PacketType, PositionType, num_inports, num_outports, 
          InputUnitType, RouteUnitType, SwitchUnitType, OutputUnitType ):

    s.num_inports  = num_inports
    s.num_outports = num_outports

    # Components
    s.input_units  = [ InputUnitType( PacketType ) 
            for _ in range( s.num_inports ) ]

    s.route_units  = [ RouteUnitType( PacketType, PositionType, s.num_outports ) 
            for i in range( s.num_inports ) ]

    s.switch_units = [ SwitchUnitType( PacketType, s.num_inports )
            for _ in range( s.num_outports ) ]
    
    s.output_units = [ OutputUnitType( PacketType )
            for _ in range( s.num_outports ) ]

  def line_trace( s ):
    pass
