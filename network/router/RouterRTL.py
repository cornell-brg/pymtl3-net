#=========================================================================
# RouteRTL.py
#=========================================================================
# Simple network-on-chip router, try to connect all the units together
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 8, 2019

from pymtl import *
from pclib.ifcs.EnRdyIfc import InEnRdyIfc, OutEnRdyIfc
from pclib.rtl  import NormalQueueRTL

from ocn_pclib.Packet    import Packet
from ocn_pclib.Position  import *

from network.router.InputUnitRTL  import InputUnitRTL
from network.router.SwitchUnitRTL import SwitchUnitRTL
from network.router.OutputUnitRTL import OutputUnitRTL


class RouterRTL( RTLComponent ):
  def construct( s, router_id, RoutingStrategyType, RouteUnitType, PositionType ):

    s.router_id = router_id
    s.num_inports  = 5
    s.num_outports = 5
    QueueType = NormalQueueRTL

    # Interface
    s.recv = [ InEnRdyIfc( Packet )  for _ in range( s.num_inports ) ]
    s.send = [ OutEnRdyIfc( Packet ) for _ in range( s.num_outports ) ]

    s.pos  = [ InVPort( PositionType ) for _ in range( s.num_inports ) ]
    s.out_dirs = [ OutVPort( Bits3 ) for _ in range( s.num_inports ) ]

    # Components

#    s.routing_logics = [ RoutingDORY( PacketType )
#                       for _ in range( s.num_inports ) ]
#    s.route_units    = [ RouteUnit( s.routing_logics[_], PositionType )
#                       for _ in range( s.num_inports ) ]

#    s.input_units  = [ InputUnitRTL( Packet )
#                     for i in range( s.num_inports ) ]

    routing_logics = [ RoutingStrategyType( Packet )
                     for _ in range( s.num_inports ) ]

    s.route_units  = [ RouteUnitType( routing_logics[i], PositionType )
                     for i in range( s.num_inports ) ]

    s.switch_units = [ SwitchUnitRTL( Packet, s.num_inports )
                     for _ in range( s.num_outports ) ]

#    s.output_units = [ OutputUnitRTL( Packet, QueueType )
#                     for _ in range( s.num_outports ) ]
#    s.output_units = [ OutputUnitRTL( Packet )

    # Connections
#    s.connect( s.recv.msg, s.route_unit.recv.msg   )
#    s.connect( s.recv,     s.route_unit.recv       )
#    s.connect( s.recv.msg, s.routing_logic.pkt_in  )
#    s.connect( s.pos,      s.routing_logic.pos     )
#    s.connect( s.output,   s.routing_logic.out_dir )

#    for i in range( s.num_outports ):
#      s.connect( s.route_unit.send[i].msg,   s.output_units[i].recv.msg )
#      s.connect( s.route_unit.send[i].en,    s.output_units[i].recv.rdy )
#      s.connect( s.output_units[i].send.rdy, s.send[i].rdy         )
#      s.connect( s.output_units[i].send, s.send[i] )

    for i in range( s.num_inports ):
#      s.connect( s.recv, s.input_units[i].recv )
#      s.connect( s.input_units[i].send, s.route_units[i].recv )
      s.connect( s.recv[i],        s.route_units[i].recv )
      s.connect( s.pos[i],      s.route_units[i].pos        )
      s.connect( s.out_dirs[i], s.route_units[i].out_dir )

    for i in range( s.num_inports ):
      for j in range( s.num_outports ):
        s.connect( s.route_units[i].send[j], s.switch_units[j].recv[i] )
#        s.connect( s.route_units[i].out[j], s.switch_units[j].in_[i] )
#
    for j in range( s.num_outports ):
#      s.connect( s.switch_units[j].send, s.output_units[j].send )
#      s.connect( s.output_units[j].send, s.send[j] )
      s.connect( s.switch_units[j].send, s.send[j] )

  # TODO: Implement line trace.
  def line_trace( s ):
    return "pos:({},{}); src:({},{}); dst:({},{}); out_dir:({})".format( 
s.pos[0].pos_x, s.pos[0].pos_y, s.recv[0].msg.src_x, s.recv[0].msg.src_y, 
s.recv[0].msg.dst_x, s.recv[0].msg.dst_y, s.out_dirs )
