#=========================================================================
# RouteUnitRTL.py
#=========================================================================
# A route unit with configurable routing strategies.
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 3, 2019

from pymtl import *
from pclib.ifcs.EnRdyIfc  import InEnRdyIfc, OutEnRdyIfc

from Packet     import Packet
#from routing.RoutingDOR import RoutingDOR
#from routing.RoutingWFR import RoutingWFR
#from routing.RoutingNLR import RoutingNLR

class RouteUnitRTL( RTLComponent ):
  def construct( s, routing_logic, num_outports=5, pos_x=0, pos_y=0):

    # Constants 
    s.num_outports = num_outports

    s.x_addr_nbits = 4
    s.y_addr_nbits = 4
    NORTH = 0
    SOUTH = 1
    WEST  = 2
    EAST  = 3
    SELF  = 4

    # Interface
    s.recv = InEnRdyIfc( Packet )
    s.send = [ OutEnRdyIfc (Packet) for _ in range ( s.num_outports ) ]

    s.pos_x = pos_x
    s.pos_y = pos_y

    # Componets
    s.routing_logic = routing_logic(Packet)

    s.src_x = Wire( Bits4 )
    s.src_y = Wire( Bits4 )

    s.out_rdys = Wire( mk_bits( s.num_outports ) )

    s.pkt     = Wire( Packet )
    s.out_dir = Wire( Bits3  ) 


    # Connections
    s.connect( s.pkt,         s.recv.msg    )
    for i in range( s.num_outports ):
      s.connect( s.recv.msg,    s.send[i].msg )
      s.connect( s.out_rdys[i], s.send[i].rdy )
    
    s.connect( s.pos_x, s.routing_logic.pos_x     )  
    s.connect( s.pos_y, s.routing_logic.pos_y     )  
    s.connect( s.pkt,   s.routing_logic.pkt_in    )
    s.connect( s.routing_logic.out_dir, s.out_dir )

    # Routing logic
    @s.update
    def routingLogic():
      for i in range( s.num_outports ):
        s.send[i].en = 0
#      if routing == 'DOR_X':
        # r = RoutingDOR( 'x' )
        # r.set_dimension( 'x' )
        # s.out_dir = r.compute_output(s.pos_x, s.pos_y, s.pkt)
      s.send[s.out_dir].en = s.recv.en
#      elif routing == 'DOR_Y':
        # r = RoutingDOR( 'y' )
        # r.set_dimension( 'y' )
        # s.out_dir = r.compute_output(s.pos_x, s.pos_y, s.pkt)
#        s.send[s.out_dir].en = s.recv.en
#      elif routing == 'WFR':
#        r = RoutingWFR()
#        s.out_dir = r.compute_output(s.pos_x, s.pos_y, s.pkt)
#        s.send[s.out_dir].en = s.recv.en
#      elif routing == 'NLR':
#        r = RoutingNLR()
#        s.out_dir = r.compute_output(s.pos_x, s.pos_y, s.pkt)
#        s.send[s.out_dir].en = s.recv.en

#      else:
#        raise AssertionError( "Invalid input for routing strategy: %s " % routing )

  def line_trace( s ):
    out_str = [ "" for _ in range( s.num_outports ) ]
    for i in range (s.num_outports):
      out_str[i] = "<{}>".format( s.send[i].en ) 
    return "pos:({},{}); src:({},{}); dst:({},{}); out_dir:({});\
 ({}|{}|{}|{}|{})".format( s.pos_x, s.pos_y, s.pkt.src_x, s.pkt.src_y, 
s.pkt.dst_x, s.pkt.dst_y, s.out_dir, out_str[0], out_str[1], out_str[2], 
out_str[3], out_str[4] )
