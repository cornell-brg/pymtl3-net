"""
==========================================================================
MeshRouterCL.py
==========================================================================
Cycle level implementation of MeshRouter.

Author : Yanghui Ou
  Date : May 16, 2019
"""
from pymtl3               import *
from router.Router        import Router
from router.InputUnitCL   import InputUnitCL
from router.SwitchUnitCL  import SwitchUnitCL
from router.OutputUnitCL  import OutputUnitCL
from .DORXMeshRouteUnitCL import DORXMeshRouteUnitCL

class MeshRouterCL( Router ):

  def construct( s,
    PacketType,
    PositionType,
    InputUnitType  = InputUnitCL,
    RouteUnitType  = DORXMeshRouteUnitCL,
    SwitchUnitType = SwitchUnitCL,
    OutputUnitType = OutputUnitCL,
  ):

    s.num_inports  = 5
    s.num_outports = 5

    # Interface
    s.pos  = InPort( PositionType )
    s.recv = [ NonBlockingCalleeIfc( PacketType ) for _ in range( s.num_inports  ) ]
    s.send = [ NonBlockingCallerIfc( PacketType ) for _ in range( s.num_outports ) ]

    # Components
    s.input_units  = [ InputUnitType( PacketType )
                      for _ in range( s.num_inports ) ]

    s.route_units  = [ RouteUnitType( PacketType, PositionType )
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

  def line_trace( s ):
    in_trace  = "|".join([ str(s.recv[i]) for i in range(5) ])
    out_trace = "|".join([ str(s.send[i]) for i in range(5) ])
    return "{}_({})_{}".format( in_trace, s.pos, out_trace )
