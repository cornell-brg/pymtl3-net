#=========================================================================
# Router.py
#=========================================================================
# A generic router model.
#
# Author : Yanghui Ou, Cheng Tan
#   Date : Mar 26, 2019

from pymtl3_net.ocnlib.ifcs.PhysicalDimension import PhysicalDimension
from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc


class Router( Component ):

  def construct( s, PacketType, PositionType, num_inports, num_outports,
                 InputUnitType, RouteUnitType, SwitchUnitType,
                 OutputUnitType ):

    s.dim = PhysicalDimension()
    s.num_inports  = num_inports
    s.num_outports = num_outports

    # Interface

    s.pos  = InPort( PositionType )
    s.recv = [ IStreamIfc( PacketType ) for _ in range( s.num_inports  ) ]
    s.send = [ OStreamIfc( PacketType ) for _ in range( s.num_outports ) ]

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
      s.input_units[i].send //= s.route_units[i].recv
      s.pos                 //= s.route_units[i].pos

    for i in range( s.num_inports ):
      for j in range( s.num_outports ):
        s.route_units[i].send[j] //= s.switch_units[j].recv[i]

    for j in range( s.num_outports ):
      s.switch_units[j].send //= s.output_units[j].recv
      s.output_units[j].send //= s.send[j]

  # Line trace

  def line_trace( s ):
    return "{}({}){}".format(
      "|".join( [ f"{x}" for x in s.recv ] ),
      s.pos,
      "|".join( [ f"{x}" for x in s.send ] )
    )

  # def elaborate_physical( s ):
  #   s.dim.w = 50
  #   s.dim.h = 150
