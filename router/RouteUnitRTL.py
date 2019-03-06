#=========================================================================
# RouteUnitRTL.py
#=========================================================================
# A route unit with configurable routing strategies.
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 3, 2019

from pymtl import *
from pclib.ifcs.EnRdyIfc  import InEnRdyIfc, OutEnRdyIfc

from ocn_pclib.Packet     import Packet

class RouteUnitRTL( RTLComponent ):
  def construct( s, RoutingLogic, num_outports=5 ):

    # Constants 
    s.num_outports = num_outports

    s.x_addr_nbits = 4
    s.y_addr_nbits = 4

    # Interface
    s.recv  = InEnRdyIfc( Packet )
    s.send  = [ OutEnRdyIfc (Packet) for _ in range ( s.num_outports ) ]
    # Position should be more generic
    s.pos_x = InVPort( Bits4 )
    s.pos_y = InVPort( Bits4 )

    # Componets
    s.routing_logic = RoutingLogic(Packet)
    s.out_rdys = Wire( mk_bits( s.num_outports ) )
    s.pkt      = Wire( Packet )
    s.out_dir  = Wire( Bits3  ) 

    # Connections
    s.connect( s.pkt,           s.recv.msg    )
    for i in range( s.num_outports ):
      s.connect( s.recv.msg,    s.send[i].msg )
      s.connect( s.out_rdys[i], s.send[i].rdy )
    
    s.connect( s.pos_x,   s.routing_logic.pos_x   )  
    s.connect( s.pos_y,   s.routing_logic.pos_y   )  
    s.connect( s.pkt,     s.routing_logic.pkt_in  )
    s.connect( s.out_dir, s.routing_logic.out_dir )

    # Routing logic
    @s.update
    def routingLogic():
      for i in range( s.num_outports ):
        s.send[i].en = 0
      s.send[s.out_dir].en = s.recv.en

  def line_trace( s ):
    out_str = [ "" for _ in range( s.num_outports ) ]
    for i in range (s.num_outports):
      out_str[i] = "<{}>".format( s.send[i].en ) 
    return "pos:({},{}); src:({},{}); dst:({},{}); out_dir:({});\
 ({}|{}|{}|{}|{})".format( s.pos_x, s.pos_y, s.pkt.src_x, s.pkt.src_y, 
s.pkt.dst_x, s.pkt.dst_y, s.out_dir, out_str[0], out_str[1], out_str[2], 
out_str[3], out_str[4] )
