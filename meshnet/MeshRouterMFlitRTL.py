'''
==========================================================================
MeshRouterMFlitRTL
==========================================================================
Mesh router that supports multi-flit packet.

Author : Yanghui Ou
  Date : Feb 13, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL
from ocnlib.utils import get_nbits
from router.InputUnitRTL import InputUnitRTL
from router.OutputUnitRTL import OutputUnitRTL
from router.SwitchUnitGrantHoldRTL import SwitchUnitGrantHoldRTL

from .MeshRouteUnitRTLMFlitXY import MeshRouteUnitRTLMFlitXY

#-------------------------------------------------------------------------
# MeshRouterMFlitRTL
#-------------------------------------------------------------------------

class MeshRouterMFlitRTL( Component ):

  #-----------------------------------------------------------------------
  # Construct
  #-----------------------------------------------------------------------

  def construct( s,
    Header,
    PositionType,
    InputUnitType  = InputUnitRTL,
    RouteUnitType  = MeshRouteUnitRTLMFlitXY,
    SwitchUnitType = SwitchUnitGrantHoldRTL,
    OutputUnitType = OutputUnitRTL,
  ):

    # Local parameter

    s.num_inports  = 5
    s.num_outports = 5
    s.PhitType     = mk_bits( get_nbits( Header ) )

    # Interface

    s.recv = [ RecvIfcRTL( s.PhitType ) for _ in range( s.num_inports  ) ]
    s.send = [ SendIfcRTL( s.PhitType ) for _ in range( s.num_outports ) ]
    s.pos  = InPort( PositionType )

    # Components

    s.input_units  = [ InputUnitType( s.PhitType )
                       for _ in range( s.num_inports ) ]

    s.route_units  = [ RouteUnitType( Header, PositionType )
                       for i in range( s.num_inports ) ]

    s.switch_units = [ SwitchUnitType( s.PhitType, s.num_inports )
                       for _ in range( s.num_outports ) ]

    s.output_units = [ OutputUnitType( s.PhitType )
                       for _ in range( s.num_outports ) ]

    # Connections

    for i in range( s.num_inports ):
      s.recv[i]             //= s.input_units[i].recv
      s.input_units[i].give //= s.route_units[i].get
      s.pos                 //= s.route_units[i].pos

    for i in range( s.num_inports ):
      for j in range( s.num_outports ):
        s.route_units[i].give[j] //= s.switch_units[j].get[i]
        s.route_units[i].hold[j] //= s.switch_units[j].hold[i]

    for j in range( s.num_outports ):
      s.switch_units[j].give //= s.output_units[j].get
      s.output_units[j].send //= s.send[j]

  #-----------------------------------------------------------------------
  # Line trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    in_trace  = '|'.join([ f'{ifc}' for ifc in s.recv ])
    out_trace = '|'.join([ f'{ifc}' for ifc in s.send ])
    return f'{in_trace}({s.pos}){out_trace}'
