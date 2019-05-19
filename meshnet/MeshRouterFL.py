#=========================================================================
# MeshRouteFL.py
#=========================================================================
# Simple network-on-chip router in FL modeling
#
# Author : Cheng Tan
#   Date : May 18, 2019

from pymtl                import *
from pclib.ifcs           import RecvIfcFL
from pclib.ifcs           import SendIfcFL

#TODO: should inherit from Component?
class MeshRouterFL( Component ):

  def construct( s, PacketType, PositionType, num_inports, num_outports,
                 RouteUnitType = 'DORY' ): 

    s.num_inports  = num_inports
    s.num_outports = num_outports

    # Interface

    s.pos = InPort( PositionType )
    s.recv = [ RecvIfcFL( PacketType ) for _ in range( s.num_inports  ) ]
    s.send = [ SendIfcFL( PacketType ) for _ in range( s.num_outports ) ]

    # Components

    s.recv_queue = [ [] for _ in range( s.num_inports ) ]
    s.next_arbiter = 0

    # Routing Logic
    @s.tick_fl
    def up_routing():

      for i in range( s.num_inports ):
        if s.recv[i].msg != None:
          s.recv_queue[i].append( s.recv[i].msg )

      current_arbiter = s.next_arbiter
      occupied_dir = []
      for _ in range( s.num_inports ):
        out_dir = 0
        index = current_arbiter % s.num_inports
        if RouteUnitType = 'DORY':
          if len( s.recv_queue[ index ] ) != 0:
            if s.pos.pos_x == s.recv_queue[ index ].msg.dst_x 
             and s.pos.pos_y == s.recv_queue[ index ].msg.dst_y:
              out_dir = SELF
            elif s.recv_queue[ index ].msg.dst_y < s.pos.pos_y:
              out_dir = SOUTH
            elif s.recv_queue[ index ].msg.dst_y > s.pos.pos_y:
              out_dir = NORTH
            elif s.recv_queue[ index ].msg.dst_x < s.pos.pos_x:
              out_dir = WEST
            else:
              out_dir = EAST
            if out_dir not in occupied_dir:
              s.send[ out_dir ].msg = s.recv_queue[ index ].pop( 0 )
              occupied_dir.append( out_dir )
            else:
              s.next_arbiter = current_arbiter
        current_arbiter += 1
      
  def line_trace( s ):

    in_trace  = [ "" for _ in range( s.num_inports  ) ]
    out_trace = [ "" for _ in range( s.num_outports ) ]

    for i in range( s.num_inports ):
      in_trace[i]  = "{}".format( s.recv[i].line_trace() )
    for i in range( s.num_outports ):
      out_trace[i] = "{}".format( s.send[i].line_trace() )

    return "{}({}){}".format(
      "|".join( in_trace ),
      s.pos,
      "|".join( out_trace )
    )

