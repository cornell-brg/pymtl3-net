"""
=========================================================================
RingRouteRTL.py
=========================================================================
Ring network-on-chip router

Author : Yanghui Ou, Cheng Tan
  Date : June 25, 2019
"""
from pymtl3                     import *
from ocn_pclib.ifcs.CreditIfc   import CreditRecvIfcRTL, CreditSendIfcRTL
from router.Router              import Router
from router.SwitchUnitRTL       import SwitchUnitRTL
from router.InputUnitCreditRTL  import InputUnitCreditRTL
from router.OutputUnitCreditRTL import OutputUnitCreditRTL
from .RingRouteUnitRTL          import RingRouteUnitRTL

class RingRouterRTL( Router ):

  def construct( s,
    PacketType,
    PositionType,
    num_routers,
    InputUnitType=InputUnitCreditRTL,
    RouteUnitType=RingRouteUnitRTL,
    SwitchUnitType=SwitchUnitRTL,
    OutputUnitType=OutputUnitCreditRTL,
    nvcs=2,
    credit_line=2,
  ):

    # Local paramters

    s.num_inports  = 3
    s.num_outports = 3
    s.nvcs = nvcs
    s.num_route_units = s.num_inports * s.nvcs

    # Interface

    s.pos  = InPort( PositionType )
    s.recv = [ CreditRecvIfcRTL( PacketType, s.nvcs ) for _ in range( s.num_inports  ) ]
    s.send = [ CreditSendIfcRTL( PacketType, s.nvcs ) for _ in range( s.num_outports ) ]

    # Components

    s.input_units  = [ InputUnitType( PacketType, nvcs=nvcs, credit_line=credit_line )
                       for _ in range( s.num_inports ) ]

    s.route_units  = [ RouteUnitType( PacketType, PositionType, num_routers )
                       for i in range( s.num_route_units ) ]

    s.switch_units = [ SwitchUnitType( PacketType, s.num_route_units )
                       for _ in range( s.num_outports ) ]

    s.output_units = [ OutputUnitType( PacketType )
                       for _ in range( s.num_outports ) ]

    # Connection

    for i in range( s.num_inports ):
      s.recv[i] //= s.input_units[i].recv
      for j in range( s.nvcs ):
        ru_idx = i * s.nvcs + j
        s.input_units[i].give[j] //= s.route_units[ru_idx].get
        s.pos                    //= s.route_units[ru_idx].pos

    for i in range( s.num_route_units ):
      for j in range( s.num_outports ):
        s.route_units[i].give[j] //= s.switch_units[j].get[i]

    for j in range( s.num_outports ):
      s.switch_units[j].give //= s.output_units[j].get
      s.output_units[j].send //= s.send[j]

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
