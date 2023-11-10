'''
==========================================================================
XbarMflitRTL.py
==========================================================================
A crossbar that supports multi-flit packet.

Author : Yanghui Ou
  Date : Feb 18, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc
from pymtl3_net.router.InputUnitRTL import InputUnitRTL
from pymtl3_net.router.OutputUnitRTL import OutputUnitRTL
from pymtl3_net.router.SwitchUnitGrantHoldRTL import SwitchUnitGrantHoldRTL
from pymtl3_net.router.SwitchUnitNullRTL import SwitchUnitNullRTL

from .XbarRouteUnitMflitRTL import XbarRouteUnitMflitRTL

#-------------------------------------------------------------------------
# XbarMflitRTL
#-------------------------------------------------------------------------

class XbarMflitRTL( Component ):

  #-----------------------------------------------------------------------
  # Construct
  #-----------------------------------------------------------------------

  def construct( s,
    Header,
    num_inports    = 2,
    num_outports   = 2,
    InputUnitType  = InputUnitRTL,
    RouteUnitType  = XbarRouteUnitMflitRTL,
    SwitchUnitType = SwitchUnitGrantHoldRTL,
    OutputUnitType = OutputUnitRTL,
  ):

    # Local parameter

    s.num_inports  = num_inports
    s.num_outports = num_outports
    s.PhitType     = mk_bits( Header.nbits )

    # Special case for num_inports = 1
    if num_inports == 1: SwitchUnitType = SwitchUnitNullRTL

    # Interface

    s.recv = [ IStreamIfc( s.PhitType ) for _ in range( s.num_inports  ) ]
    s.send = [ OStreamIfc( s.PhitType ) for _ in range( s.num_outports ) ]

    # Components

    s.input_units = [ InputUnitType( s.PhitType )
                      for _ in range( s.num_inports )  ]

    s.route_units  = [ RouteUnitType( Header, s.num_outports )
                       for i in range( s.num_inports ) ]

    s.switch_units = [ SwitchUnitType( s.PhitType, s.num_inports )
                       for _ in range( s.num_outports ) ]

    s.output_units = [ OutputUnitType( s.PhitType )
                       for _ in range( s.num_outports ) ]

    # Connections

    for i in range( s.num_inports ):
      s.recv[i]             //= s.input_units[i].recv
      s.input_units[i].send //= s.route_units[i].recv

    for i in range( s.num_inports ):
      for j in range( s.num_outports ):
        s.route_units[i].send[j] //= s.switch_units[j].recv[i]
        s.route_units[i].hold[j] //= s.switch_units[j].hold[i]

    for j in range( s.num_outports ):
      s.switch_units[j].send //= s.output_units[j].recv
      s.output_units[j].send //= s.send[j]

  #-----------------------------------------------------------------------
  # Line trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    in_trace  = '|'.join([ f'{ifc}' for ifc in s.recv ])
    out_trace = '|'.join([ f'{ifc}' for ifc in s.send ])
    return f'{in_trace}(){out_trace}'
