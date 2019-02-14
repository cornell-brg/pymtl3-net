from pymtl import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from ifcs.SinglePhitPacket import SinglePhitPacket
from router.InputUnit    import InputUnit
from router.RouteUnitDOR import RouteUnitDOR
from router.SwitchUnit   import SwitchUnit
from router.OutputUnit   import OutputUnit

class MeshRouterSphit( Model ):

  def __init__( s, pkt_type, dimension,
                input_queue_size=2, output_queue_size=0 ):

    # Sanity Check
    if dimension.lower() != 'x' and dimension.lower() != 'y':
      raise AssertionError( "Invalid routing dimension %s!" % dimension )
    
    # Constants 
    s.num_inports  = 5
    s.num_outports = 5
    s.addr_x_nbits = pkt_type.dst_x.nbits
    s.addr_y_nbits = pkt_type.dst_y.nbits
    
    # Interface
    s.in_   =  InValRdyBundle[ s.num_inports  ]( pkt_type )
    s.out   = OutValRdyBundle[ s.num_outports ]( pkt_type )
    s.pos_x = Wire( s.addr_x_nbits )
    s.pos_y = Wire( s.addr_y_nbits )

    # Components
    s.input_units  = [ InputUnit( input_queue_size, pkt_type ) 
                       for _ in range( s.num_inports ) ]
    s.route_units  = [ RouteUnitDOR( pkt_type, dimension )
                       for _ in range( s.num_inports ) ]
    s.switch_units = [ SwitchUnit( pkt_type, s.num_inports )
                       for _ in range( s.num_outports ) ]
    s.output_units = [ OutputUnit( output_queue_size, pkt_type )
                       for _ in range( s.num_outports ) ]

    # Connections
    for i in range( s.num_inports ):
      s.connect( s.in_[i], s.input_units[i].in_ )
      s.connect( s.input_units[i].out, s.route_units[i].in_ )
      s.connect( s.pos_x, s.route_units[i].pos_x )
      s.connect( s.pos_y, s.route_units[i].pos_y )
    
    for i in range( s.num_inports ):
      for j in range( s.num_outports ):
        s.connect( s.route_units[i].out[j], s.switch_units[j].in_[i] )

    for j in range( s.num_outports ):
      s.connect( s.switch_units[j].out, s.output_units[j].in_ )
      s.connect( s.output_units[j].out, s.out[j]              )
    
    # TODO: Implement line trace.
  def line_trace( s ):
    in_str = [ "" for _ in range( 5 ) ]
    for i in range( 5 ):
      in_str[i] = s.in_[i].to_str( "%1s:(%1s,%1s)>(%1s,%1s)" % 
                                  ( s.in_[i].msg.opaque, 
                                    s.in_[i].msg.src_x, s.in_[i].msg.src_y, 
                                    s.in_[i].msg.dst_x, s.in_[i].msg.dst_y ) )
    return "({},{})({}|{}|{}|{}|{})".format( s.pos_x, s.pos_y, 
                                              in_str[0], in_str[1], in_str[2], in_str[3], in_str[4]  )  
