#=========================================================================
# RingRouteCL.py
#=========================================================================
# Ring network-on-chip router
#
# Author : Yanghui Ou
#   Date : May 16, 2019

from pymtl import *
from pclib.ifcs.GuardedIfc import GuardedCalleeIfc, GuardedCallerIfc
from router.Router       import Router
from router.InputUnitCL  import InputUnitCL
from router.SwitchUnitCL import SwitchUnitCL
from router.OutputUnitCL import OutputUnitCL
from RingRouteUnitCL     import RingRouteUnitCL

class RingRouterCL( Router ):

  def construct( s, 
                 PacketType, 
                 PositionType,
                 InputUnitType  = InputUnitCL, 
                 RouteUnitType  = RingRouteUnitCL, 
                 SwitchUnitType = SwitchUnitCL, 
                 OutputUnitType = OutputUnitCL, 
                 #RecvIfcType = GuardedCalleeIfc,
                 #SendIfcType = GuardedCallerIfc,
                 ):

    s.num_inports  = 3
    s.num_outports = 3

    # Interface
    s.pos  = InPort( PositionType ) 
    s.recv = [ GuardedCalleeIfc() for _ in range( s.num_inports  ) ]
    s.send = [ GuardedCallerIfc() for _ in range( s.num_outports ) ]
    
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
      "|".join( [ s.input_units[i].line_trace()  for i in range(3) ] ), 
      "|".join( [ s.route_units[i].line_trace() for i in range(3) ] ), 
      #"|".join( [ s.switch_units[i].line_trace() for i in range(3) ] ), 
    )
