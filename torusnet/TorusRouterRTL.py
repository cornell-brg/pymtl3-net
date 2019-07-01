"""
==========================================================================
TorusRouterRTL.py
==========================================================================
Torus router RTL model.

Author : Yanghui, Ou, Cheng Tan
  Date : June 30, 2019
"""
from pymtl3                     import *
from ocn_pclib.ifcs.CreditIfc   import CreditRecvIfcRTL, CreditSendIfcRTL
from router.SwitchUnitRTL       import SwitchUnitRTL
from router.InputUnitCreditRTL  import InputUnitCreditRTL
from router.OutputUnitCreditRTL import OutputUnitCreditRTL
from DORYTorusRouteUnitRTL      import DORYTorusRouteUnitRTL

class TorusRouterRTL( Component ):

  def construct( s,
    PacketType,
    PositionType,
    InputUnitType=InputUnitCreditRTL,
    RouteUnitType=DORYTorusRouteUnitRTL,
    SwitchUnitType=SwitchUnitRTL,
    OutputUnitType=OutputUnitCreditRTL,
    ncols=2,
    nrows=2,
    nvcs=2,
    credit_line=2,
  ):

    s.num_inports  = 5
    s.num_outports = 5
    s.nvcs = nvcs
    s.num_route_units = s.num_inports * s.nvcs

    # Interface

    s.pos  = InPort( PositionType )
    s.recv = [ CreditRecvIfcRTL( PacketType, s.nvcs ) for _ in range( s.num_inports  ) ]
    s.send = [ CreditSendIfcRTL( PacketType, s.nvcs ) for _ in range( s.num_outports ) ]

    # Components

    s.input_units  = [ InputUnitType( PacketType, nvcs=nvcs, credit_line=credit_line )
                      for _ in range( s.num_inports ) ]

    s.route_units  = [ RouteUnitType( PacketType, PositionType, ncols, nrows )
                      for i in range( s.num_route_units ) ]

    s.switch_units = [ SwitchUnitType( PacketType, s.num_route_units )
                      for _ in range( s.num_outports ) ]

    s.output_units = [ OutputUnitType( PacketType )
                      for _ in range( s.num_outports ) ]

    # Connection

    for i in range( s.num_inports ):
      s.connect( s.recv[i], s.input_units[i].recv )
      for j in range( s.nvcs ):
        ru_idx = i * s.nvcs + j
        s.connect( s.input_units[i].give[j], s.route_units[ru_idx].get  )
        s.connect( s.pos,                    s.route_units[ru_idx].pos  )

    for i in range( s.num_route_units ):
      for j in range( s.num_outports ):
        s.connect( s.route_units[i].give[j], s.switch_units[j].get[i] )

    for j in range( s.num_outports ):
      s.connect( s.switch_units[j].give, s.output_units[j].get )
      s.connect( s.output_units[j].send, s.send[j]              )

  # Line trace

  def line_trace( s ):
    in_trace  = [ "" for _ in range( s.num_inports  ) ]
    out_trace = [ "" for _ in range( s.num_outports ) ]

    for i in range( s.num_inports ):
      in_trace[i]  = "{}".format( s.recv[i] )
    for i in range( s.num_outports ):
      out_trace[i] = "{}".format( s.send[i] )

    return "{}_({})_{}".format(
      "|".join( in_trace ),
      s.pos,
      "|".join( out_trace )
    )

  def elaborate_physical( s ):
    s.dim.w = 50
    s.dim.h = 50
