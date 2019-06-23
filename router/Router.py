#=========================================================================
# Router.py
#=========================================================================
# A generic router model.
#
# Author : Yanghui Ou, Cheng Tan
#   Date : Mar 26, 2019

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL

class Router( Component ):

  def construct( s, PacketType, PositionType, num_inports, num_outports,
                 InputUnitType, RouteUnitType, SwitchUnitType,
                 OutputUnitType ):

    s.num_inports  = num_inports
    s.num_outports = num_outports

    # Interface

    s.pos  = InPort( PositionType )
    s.recv = [ RecvIfcRTL( PacketType ) for _ in range( s.num_inports  ) ]
    s.send = [ SendIfcRTL( PacketType ) for _ in range( s.num_outports ) ]

    # Components

    s.input_units  = [ InputUnitType( PacketType )
                      for _ in range( s.num_inports ) ]

    s.route_units  = [ RouteUnitType( PacketType, PositionType, s.num_outports )
                      for i in range( s.num_inports ) ]

    s.switch_units = [ SwitchUnitType( PacketType, s.num_inports )
                      for _ in range( s.num_outports ) ]

    s.output_units = [ OutputUnitType( PacketType )
                      for _ in range( s.num_outports ) ]

    # Connection

    for i in range( s.num_inports ):
      s.connect( s.recv[i],             s.input_units[i].recv )
      s.connect( s.input_units[i].give, s.route_units[i].get  )
      s.connect( s.pos,                 s.route_units[i].pos  )

    for i in range( s.num_inports ):
      for j in range( s.num_outports ):
        s.connect( s.route_units[i].give[j], s.switch_units[j].get[i] )

    for j in range( s.num_outports ):
#      s.connect( s.switch_units[j].send, s.output_units[j].recv )
      s.connect( s.switch_units[j].give, s.output_units[j].get )
      s.connect( s.output_units[j].send, s.send[j]              )

  # Line trace

  def line_trace( s ):

    in_trace  = [ "" for _ in range( s.num_inports  ) ]
    out_trace = [ "" for _ in range( s.num_outports ) ]

    for i in range( s.num_inports ):
      in_trace[i]  = "{}".format( s.recv[i].line_trace() )
    for i in range( s.num_outports ):
      out_trace[i] = "{}".format( s.send[i].line_trace() )

    return "{}({}){}".format(
      "|".join( in_trace ),
      s.pos,
      "|".join( out_trace )
    )

  def elaborate_physical( s ):
    s.dim.w = 50
    s.dim.h = 50
