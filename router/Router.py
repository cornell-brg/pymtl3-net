#=========================================================================
# Router.py
#=========================================================================
# A generic router model.
#
# Author : Yanghui Ou, Cheng Tan
#   Date : Mar 26, 2019

from ocn_pclib.ifcs.PhysicalDimension import PhysicalDimension
from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL


class Router( Component ):

  def construct( s, PacketType, PositionType, num_inports, num_outports,
                 InputUnitType, RouteUnitType, SwitchUnitType,
                 OutputUnitType ):

    s.dim = PhysicalDimension()
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
      s.recv[i]             //= s.input_units[i].recv
      s.input_units[i].give //= s.route_units[i].get
      s.pos                 //= s.route_units[i].pos

    for i in range( s.num_inports ):
      for j in range( s.num_outports ):
        s.route_units[i].give[j] //= s.switch_units[j].get[i]

    for j in range( s.num_outports ):
      s.switch_units[j].give //= s.output_units[j].get
      s.output_units[j].send //= s.send[j]

  # Line trace

  def line_trace( s ):
    return "{}({}){}".format(
      "|".join( [ f"{x.line_trace()}" for x in s.recv ] ),
      s.pos,
      "|".join( [ f"{x.line_trace()}" for x in s.send ] )
    )

  def elaborate_physical( s ):
    s.dim.w = 50
    s.dim.h = 150
