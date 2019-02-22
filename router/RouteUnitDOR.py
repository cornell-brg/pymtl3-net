#=========================================================================
# RouteUnitDOR.py
#=========================================================================
# A route unit implementing dimension-order routing.
#
# Author : Yanghui Ou, Cheng Tan
#   Date : Feb 14, 2019

from pymtl import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle

class RouteUnitDOR( Model ):
  def __init__( s, msg_type, dimension ):

    # Constants 
    s.num_outports = 5
    s.x_addr_nbits = msg_type.dst_x.nbits
    s.y_addr_nbits = msg_type.dst_y.nbits 
    NORTH = 0
    SOUTH = 1
    WEST  = 2
    EAST  = 3
    SELF  = 4

    # Interface
    s.in_ =  InValRdyBundle( msg_type )
    s.out = OutValRdyBundle[ s.num_outports ]( msg_type )
    s.pos_x = InPort( s.x_addr_nbits )
    s.pos_y = InPort( s.y_addr_nbits )

    # Componets
    s.out_rdys = Wire( s.num_outports )
    s.dst_x    = Wire( s.x_addr_nbits )
    s.dst_y    = Wire( s.y_addr_nbits )

    # Connections
    for i in range( s.num_outports ):
      s.connect( s.in_.msg,       s.out[i].msg )
      s.connect( s.out_rdys[i],   s.out[i].rdy )
      s.connect( s.in_.msg.dst_x, s.dst_x      )
      s.connect( s.in_.msg.dst_y, s.dst_y      )
    
    @s.combinational
    def assignInRdy():
      s.in_.rdy.value = reduce_or( s.out_rdys )

    # Routing logic
    @s.combinational
    def routingLogic():
      if dimension.lower() == 'x':
        for i in range( s.num_outports ):
          s.out[i].val.value = 0
        if s.pos_x == s.dst_x and s.pos_y == s.dst_y:
          s.out[SELF].val.value  = s.in_.val
        elif s.dst_x < s.pos_x:
          s.out[NORTH].val.value = s.in_.val
        elif s.dst_x > s.pos_x:
          s.out[SOUTH].val.value = s.in_.val
        elif s.dst_y < s.pos_y:
          s.out[WEST].val.value  = s.in_.val
        else:
          s.out[EAST].val.value  = s.in_.val

      elif dimension.lower() == 'y':
        for i in range( s.num_outports ):
          s.out[i].val.value = 0
        if s.pos_x == s.dst_x and s.pos_y == s.dst_y:
          s.out[SELF].val.value  = s.in_.val
        elif s.dst_y < s.pos_y:
          s.out[WEST].val.value = s.in_.val
        elif s.dst_y > s.pos_y:
          s.out[EAST].val.value = s.in_.val
        elif s.dst_x < s.pos_x:
          s.out[NORTH].val.value  = s.in_.val
        else:
          s.out[SOUTH].val.value  = s.in_.val

      else:
        raise AssertionError( "Invalid input for dimension: %s " % dimension )

  def line_trace( s ):
    out_str = [ "" for _ in range( 5 ) ]
    for i in range( 5 ):
      out_str[i] = s.out[i].to_str( "{}:<{},{}>".format( 
          s.out[i].msg.opaque, s.out[i].msg.dst_x, s.out[i].msg.dst_y ) )
    return "({},{})({}||{}|{}|{}|{}|{})".format(
        s.pos_x, s.pos_y, s.in_, 
        out_str[0], out_str[1], out_str[2], out_str[3], out_str[4] )
