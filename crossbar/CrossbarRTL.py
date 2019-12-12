"""
==========================================================================
CrossbarRTL.py
==========================================================================
Crossbar implementation.

Author : Cheng Tan
  Date : April 6, 2019
"""
from CrossbarRouteUnitRTL import CrossbarRouteUnitRTL
from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL
from router.InputUnitRTL import InputUnitRTL
from router.OutputUnitRTL import OutputUnitRTL
from router.SwitchUnitRTL import SwitchUnitRTL


class CrossbarRTL( Component ):
  def construct( s, PacketType, num_terminals=4,
                 InputUnitType  = InputUnitRTL,
                 RouteUnitType  = CrossbarRouteUnitRTL,
                 SwitchUnitType = SwitchUnitRTL,
                 OutputUnitType = OutputUnitRTL ):

    # Constants

    s.num_terminals = num_terminals
    s.num_inports   = num_terminals
    s.num_outports  = num_terminals

    # Interface

    s.recv = [ RecvIfcRTL( PacketType ) for _ in range( s.num_inports  ) ]
    s.send = [ SendIfcRTL( PacketType ) for _ in range( s.num_outports ) ]

    # Components

    s.input_units  = [ InputUnitType( PacketType )
                       for _ in range( s.num_inports ) ]

    s.route_units  = [ RouteUnitType( PacketType, s.num_outports )
                       for i in range( s.num_inports ) ]

    s.switch_units = [ SwitchUnitType( PacketType, s.num_inports )
                       for _ in range( s.num_outports ) ]

    s.output_units = [ OutputUnitType( PacketType )
                       for _ in range( s.num_outports ) ]

    # Connection

    for i in range( s.num_inports ):
      s.connect( s.recv[i],             s.input_units[i].recv )
      s.connect( s.input_units[i].give, s.route_units[i].get  )

    for i in range( s.num_inports ):
      for j in range( s.num_outports ):
        s.connect( s.route_units[i].give[j], s.switch_units[j].get[i] )

    for j in range( s.num_outports ):
      s.connect( s.switch_units[j].send, s.output_units[j].recv )
      s.connect( s.output_units[j].send, s.send[j]              )

  def line_trace( s ):
    trace = "|".join([ str(s.send[i]) for i in range( s.num_terminals ) ])
    return trace
