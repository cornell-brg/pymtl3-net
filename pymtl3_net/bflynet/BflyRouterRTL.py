"""
=========================================================================
BfRouteRTL.py
=========================================================================
RTL router for butterfly network.

Author : Cheng Tan, Yanghui Ou
  Date : April 6, 2019
"""
from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import RecvIfcRTL, SendIfcRTL

from pymtl3_net.ocnlib.ifcs.PhysicalDimension import PhysicalDimension
from pymtl3_net.router.InputUnitRTL import InputUnitRTL
from pymtl3_net.router.OutputUnitRTL import OutputUnitRTL
from pymtl3_net.router.Router import Router
from pymtl3_net.router.SwitchUnitRTL import SwitchUnitRTL

from .DTRBflyRouteUnitRTL import DTRBflyRouteUnitRTL


class BflyRouterRTL( Component ):

  def construct( s,
    PacketType, PositionType, k_ary, n_fly,
    InputUnitType  = InputUnitRTL,
    RouteUnitType  = DTRBflyRouteUnitRTL,
    SwitchUnitType = SwitchUnitRTL,
    OutputUnitType = OutputUnitRTL,
  ):

    s.dim = PhysicalDimension()
    s.num_inports  = k_ary
    s.num_outports = k_ary

    # Interface

    s.pos  = InPort( PositionType )
    s.recv = [ RecvIfcRTL( PacketType ) for _ in range( s.num_inports  ) ]
    s.send = [ SendIfcRTL( PacketType ) for _ in range( s.num_outports ) ]

    # Components

    s.input_units  = [ InputUnitType( PacketType )
                      for _ in range( s.num_inports ) ]

    s.route_units  = [ RouteUnitType( PacketType, PositionType, s.num_outports, n_fly=n_fly )
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

  def elaborate_physical( s ):
    s.dim.w = 50
    s.dim.h = 150
