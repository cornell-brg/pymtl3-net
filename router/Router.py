#=========================================================================
# Router.py
#=========================================================================
# A generic router model. 
#
# Author : Yanghui Ou, Cheng Tan
#   Date : Mar 26, 2019

from pymtl      import *
from pclib.ifcs import SendIfcRTL, RecvIfcRTL 

class Router( ComponentLevel6 ):

  def construct( s, PacketType, PositionType, num_inports, num_outports, 
                 InputUnitType, RouteUnitType, SwitchUnitType, 
                 OutputUnitType ):

    s.num_inports  = num_inports
    s.num_outports = num_outports

    # Interface

    s.pos  = InVPort( PositionType ) 
    s.recv = [ RecvIfcRTL( PacketType ) for _ in range( s.num_inports  ) ]
    s.send = [ SendIfcRTL( PacketType ) for _ in range( s.num_outports ) ]
    
    # Components

    s.input_unit  = [ InputUnitType( PacketType ) 
                      for _ in range( s.num_inports ) ]

    s.route_unit  = [ RouteUnitType( PacketType, PositionType, s.num_outports ) 
                      for i in range( s.num_inports ) ]

    s.switch_unit = [ SwitchUnitType( PacketType, s.num_inports )
                      for _ in range( s.num_outports ) ]
    
    s.output_unit = [ OutputUnitType( PacketType )
                      for _ in range( s.num_outports ) ]
    
    # Connection
    
    for i in range( s.num_inports ):
      s.connect( s.recv[i],            s.input_unit[i].recv )
      s.connect( s.input_unit[i].send, s.route_unit[i].recv )
      s.connect( s.pos,                s.route_unit[i].pos  )
    
    for i in range( s.num_inports ):
      for j in range( s.num_inports ):
      s.connect( s.route_unit[i].send[j], s.switch_unit[j].recv[i] )

    for i in range( s.num_inports ):
      s.connect( s.switch_unit[i].send, s.output_unit[i].recv )
      s.connect( s.output_unit[i].send, s.send                )

  # Line trace

  def line_trace( s ):

    in_trace  = [ "" for _ in range( s.num_inports  ) ]
    out_trace = [ "" for _ in range( s.num_outports ) ]

    for i in range( s.num_inports ):
      s.in_trace  = "{}".format( s.recv[i] )
    for i in range( s.num_outports ):
      s.out_trace = "{}".format( s.send[i] )
      
    return "{}({}){}".format( 
      "|".join( in_trace ), s.pos, "|".join( out_trace )
    )  
