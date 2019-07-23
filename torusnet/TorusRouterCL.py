#=========================================================================
# TorusRouterCL.py
#=========================================================================
# Torus network-on-chip router in CL modeling
#
# Author : Cheng Tan
#   Date : May 20, 2019

from pymtl3 import *
from router.Router         import Router
from router.InputUnitCL    import InputUnitCL
from router.SwitchUnitCL   import SwitchUnitCL
from router.OutputUnitCL   import OutputUnitCL
from DORYTorusRouteUnitCL  import DORYTorusRouteUnitCL

class TorusRouterCL( Router ):

  def construct( s,
                 PacketType,
                 PositionType,
                 InputUnitType  = InputUnitCL,
                 RouteUnitType  = DORYTorusRouteUnitCL,
                 SwitchUnitType = SwitchUnitCL,
                 OutputUnitType = OutputUnitCL,
                 #RecvIfcType = GuardedCalleeIfc,
                 #SendIfcType = GuardedCallerIfc,
                 ):

    s.num_inports  = 5
    s.num_outports = 5

    # Interface
    s.pos  = InPort( PositionType )
    s.recv = [ NonBlockingCalleeIfc() for _ in range( s.num_inports  ) ]
    s.send = [ NonBlockingCallerIfc() for _ in range( s.num_outports ) ]

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
      s.connect( s.recv[i],             s.input_units[i].recv )
      s.connect( s.input_units[i].give, s.route_units[i].get  )
      s.connect( s.pos,                 s.route_units[i].pos  )

    for i in range( s.num_inports ):
      for j in range( s.num_outports ):
        s.connect( s.route_units[i].give[j], s.switch_units[j].get[i] )

    for j in range( s.num_outports ):
      s.connect( s.switch_units[j].send, s.output_units[j].recv )
      s.connect( s.output_units[j].send, s.send[j]              )

  def line_trace( s ):
    return "{}>{}".format(
      "|".join( [ s.input_units[i].line_trace()  for i in range(5) ] ),
      "|".join( [ s.route_units[i].line_trace() for i in range(5) ] ),
      #"|".join( [ s.switch_units[i].line_trace() for i in range(3) ] ),
    )
