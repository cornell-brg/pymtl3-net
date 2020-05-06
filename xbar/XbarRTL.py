'''
==========================================================================
XbarRTL.py
==========================================================================
A crossbar that supports single-flit packet.

Author : Yanghui Ou
  Date : Apr 16, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL
from router.InputUnitRTL import InputUnitRTL
from router.OutputUnitRTL import OutputUnitRTL
from router.SwitchUnitRTL import SwitchUnitRTL
from router.SwitchUnitNullRTL import SwitchUnitNullRTL

from .XbarRouteUnitRTL import XbarRouteUnitRTL

class XbarRTL( Component ):

  def construct( s,
    PacketType,
    num_inports    = 2,
    num_outports   = 2,
    InputUnitType  = InputUnitRTL,
    RouteUnitType  = XbarRouteUnitRTL,
    SwitchUnitType = SwitchUnitRTL,
    OutputUnitType = OutputUnitRTL,
  ):

    # Local parameter

    s.num_inports  = num_inports
    s.num_outports = num_outports

    # Special case for num_inports = 1
    if num_inports == 1: SwitchUnitType = SwitchUnitNullRTL

    # Interface

    s.recv = [ RecvIfcRTL( PacketType ) for _ in range( s.num_inports  ) ]
    s.send = [ SendIfcRTL( PacketType ) for _ in range( s.num_outports ) ]

    # Components

    s.input_units = [ InputUnitType( PacketType )
                      for _ in range( s.num_inports )  ]

    s.route_units  = [ RouteUnitType( PacketType, s.num_outports )
                       for i in range( s.num_inports ) ]

    s.switch_units = [ SwitchUnitType( PacketType, s.num_inports )
                       for _ in range( s.num_outports ) ]

    s.output_units = [ OutputUnitType( PacketType )
                       for _ in range( s.num_outports ) ]

    # Connections

    for i in range( s.num_inports ):
      s.recv[i]             //= s.input_units[i].recv
      s.input_units[i].give //= s.route_units[i].get

    for i in range( s.num_inports ):
      for j in range( s.num_outports ):
        s.route_units[i].give[j] //= s.switch_units[j].get[i]

    for j in range( s.num_outports ):
      s.switch_units[j].give //= s.output_units[j].get
      s.output_units[j].send //= s.send[j]

  #-----------------------------------------------------------------------
  # Line trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    in_trace  = '|'.join([ f'{ifc}' for ifc in s.recv ])
    out_trace = '|'.join([ f'{ifc}' for ifc in s.send ])
    return f'{in_trace}(){out_trace}'
