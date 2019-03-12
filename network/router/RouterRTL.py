#=========================================================================
# RouteRTL.py
#=========================================================================
# Simple network-on-chip router, try to connect all the units together
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 8, 2019

from pymtl import *
from pclib.ifcs.EnRdyIfc import InEnRdyIfc, OutEnRdyIfc

from ocn_pclib.Packet    import Packet
from ocn_pclib.Position  import *

class RouterRTL( RTLComponent ):
  def construct( s, router_id, RoutingStrategyType, RouteUnitType, PositionType ):

    s.num_outports = 5
    s.router_id = router_id

    # Interface
    s.recv = InEnRdyIfc( Packet )
    s.send = [ OutEnRdyIfc (Packet) for _ in range ( s.num_outports ) ]

    s.pos  = InVPort( PositionType )
    s.output = OutVPort( Bits3 )

    # Components
    s.routing_logic = RoutingStrategyType( Packet )
    s.route_unit = RouteUnitType( PositionType )

#    s.input_units    = [ InputUnit( PacketType, QueueType )
#                       for _ in range( s.num_inports ) ]
#    s.routing_logics = [ RoutingDORY( PacketType )
#                       for _ in range( s.num_inports ) ]
#    s.route_units    = [ RouteUnit( s.routing_logics[_], PositionType )
#                       for _ in range( s.num_inports ) ]
#    s.switch_units   = [ SwitchUnit( pkt_type, s.num_inports )
#                       for _ in range( s.num_outports ) ]
#    s.output_units   = [ OutputUnit( output_queue_size, pkt_type )
#                       for _ in range( s.num_outports ) ]

    # Connections
    s.connect( s.recv.msg, s.route_unit.recv.msg   )
    s.connect( s.recv.msg, s.routing_logic.pkt_in  )
    s.connect( s.pos,      s.route_unit.pos        )
    s.connect( s.pos,      s.routing_logic.pos     )
    s.connect( s.output,   s.routing_logic.out_dir )

    for i in range( s.num_outports ):
      s.connect( s.route_unit.send[i].rdy, s.send[i].rdy )
      s.connect( s.route_unit.send[i].msg, s.send[i].msg )

#    for i in range( s.num_inports ):
#      s.connect( s.recv[i], s.input_units[i].in_ )
#      s.connect( s.input_units[i].out, s.route_units[i].in_ )
#      s.connect( s.pos_x, s.route_units[i].pos_x )
#      s.connect( s.pos_y, s.route_units[i].pos_y )
#
#    for i in range( s.num_inports ):
#      for j in range( s.num_outports ):
#        s.connect( s.route_units[i].out[j], s.switch_units[j].in_[i] )
#
#    for j in range( s.num_outports ):
#      s.connect( s.switch_units[j].out, s.output_units[j].in_ )
#      s.connect( s.output_units[j].out, s.out[j]              )

  # TODO: Implement line trace.
  def line_trace( s ):
    return "pos:({},{}); src:({},{}); dst:({},{}); out_dir:({})".format( 
s.pos.pos_x, s.pos.pos_y, s.recv.msg.src_x, s.recv.msg.src_y, s.recv.msg.dst_x, 
s.recv.msg.dst_y, s.output )
