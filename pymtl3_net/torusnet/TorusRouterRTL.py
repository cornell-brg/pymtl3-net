"""
==========================================================================
TorusRouterRTL.py
==========================================================================
Torus router RTL model.

Author : Yanghui, Ou, Cheng Tan
  Date : June 30, 2019
"""
from pymtl3_net.ocnlib.ifcs.CreditIfc import CreditRecvIfcRTL, CreditSendIfcRTL
from pymtl3 import *
from pymtl3_net.router.InputUnitCreditRTL import InputUnitCreditRTL
from pymtl3_net.router.OutputUnitCreditRTL import OutputUnitCreditRTL
from pymtl3_net.router.SwitchUnitRTL import SwitchUnitRTL

from .DORYTorusRouteUnitRTL import DORYTorusRouteUnitRTL


class TorusRouterRTL( Component ):

  def construct( s, PacketType, PositionType,
                    InputUnitType=InputUnitCreditRTL,
                    RouteUnitType=DORYTorusRouteUnitRTL,
                    SwitchUnitType=SwitchUnitRTL,
                    OutputUnitType=OutputUnitCreditRTL,
                    ncols=2, nrows=2, vc=2, credit_line=2,
  ):

    s.num_inports  = 5
    s.num_outports = 5
    s.vc = vc
    s.num_route_units = s.num_inports * s.vc

    # Interface

    s.pos  = InPort( PositionType )
    s.recv = [ CreditRecvIfcRTL( PacketType, s.vc ) for _ in range( s.num_inports  ) ]
    s.send = [ CreditSendIfcRTL( PacketType, s.vc ) for _ in range( s.num_outports ) ]

    # Components

    s.input_units  = [ InputUnitType( PacketType, vc=vc, credit_line=credit_line )
                      for _ in range( s.num_inports ) ]

    s.route_units  = [ RouteUnitType( PacketType, PositionType, ncols, nrows )
                      for _ in range( s.num_route_units ) ]

    s.switch_units = [ SwitchUnitType( PacketType, s.num_route_units )
                      for _ in range( s.num_outports ) ]

    s.output_units = [ OutputUnitType( PacketType )
                      for _ in range( s.num_outports ) ]

    # Connection

    for i in range( s.num_inports ):
      s.recv[i] //= s.input_units[i].recv
      for j in range( s.vc ):
        ru_idx = i * s.vc + j
        s.input_units[i].send[j] //= s.route_units[ru_idx].recv
        s.pos                    //= s.route_units[ru_idx].pos

    for i in range( s.num_route_units ):
      for j in range( s.num_outports ):
        s.route_units[i].send[j] //= s.switch_units[j].recv[i]

    for j in range( s.num_outports ):
      s.switch_units[j].send//= s.output_units[j].recv
      s.output_units[j].send //= s.send[j]

  # Line trace

  def line_trace( s ):
    return "{}({}){}".format(
      "|".join( [ f"{str(x)}" for x in s.recv ] ),
      s.pos,
      "|".join( [ f"{str(x)}" for x in s.send ] )
    )
  def elaborate_physical( s ):
    s.dim.w = 50
    s.dim.h = 50
