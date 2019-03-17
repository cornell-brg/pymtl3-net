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

from network.router.InputUnitRTL  import InputUnitRTL
from network.router.RouteUnitRTL  import RouteUnitRTL
from network.router.SwitchUnitRTL import SwitchUnitRTL
from network.router.OutputUnitRTL import OutputUnitRTL

class RouterRTL( RTLComponent ):
  def construct( s, router_id, RoutingStrategyType, PositionType, num_inports=5, 
                 num_outports=5 ):

    s.router_id    = router_id
    s.num_inports  = num_inports
    s.num_outports = num_outports

    # Interface
    s.recv  = [  InEnRdyIfc( Packet ) for _ in range( s.num_inports  ) ]
    s.send  = [ OutEnRdyIfc( Packet ) for _ in range( s.num_outports ) ]

    s.outs  = [ OutVPort    ( Bits3 ) for _ in range( s.num_inports  ) ]
    s.pos   = InVPort( PositionType )

    # Components
    # TODO: modify InputUnit to adapt Packet
    s.input_units  = [ InputUnitRTL( Packet )
                     for _ in range( s.num_inports ) ]

    routing_logics = [ RoutingStrategyType( Packet )
                     for _ in range( s.num_inports ) ]

    s.route_units  = [ RouteUnitRTL( routing_logics[i], PositionType )
                     for i in range( s.num_inports ) ]

    s.switch_units = [ SwitchUnitRTL( Packet, s.num_inports )
                     for _ in range( s.num_outports ) ]
    
    # TODO: modify OutputUnit to adapt Packet
    s.output_units = [ OutputUnitRTL( Packet )
                     for _ in range( s.num_outports ) ]

    # Connections
    for i in range( s.num_inports ):
      s.connect(      s.recv[i],        s.input_units[i].recv    )
      s.connect( s.input_units[i].send, s.route_units[i].recv    )
      s.connect(       s.pos,           s.route_units[i].pos     )
      s.connect(      s.outs[i],        s.route_units[i].out_dir )

    for i in range( s.num_inports ):
      for j in range( s.num_outports ):
        s.connect( s.route_units[i].send[j], s.switch_units[j].recv[i] )

    for j in range( s.num_outports ):
      s.connect( s.switch_units[j].send, s.output_units[j].recv )
      s.connect( s.output_units[j].send,       s.send[j]        )

  # TODO: Implement line trace.
  def line_trace( s ):
    tmp_str =  "({},{}):".format( s.pos.pos_x, s.pos.pos_y )
    out_str = [ "" for _ in range( s.num_inports ) ]
    for i in range (s.num_inports):
      out_str[i] = " {}->({},{})".format( i, s.recv[i].msg.dst_x, s.recv[i].msg.dst_y )
      tmp_str += out_str[i]
    tmp_str += ' recv.rdy:<'
    for i in range (s.num_inports):
      tmp_str += "{}".format(s.input_units[i].recv.rdy)
    tmp_str += '> send.en:<'
    for i in range (s.num_outports):
      tmp_str += "{}".format(s.send[i].en)
    tmp_str += ">"
    return tmp_str
