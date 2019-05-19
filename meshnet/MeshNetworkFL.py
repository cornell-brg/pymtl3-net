#=========================================================================
# MeshNetworkFL.py
#=========================================================================
# Mesh network implementation in FL modeling.
#
# Author : Cheng Tan
#   Date : Mar 10, 2019

from pymtl                   import *
from pclib.ifcs              import RecvIfcRTL
from pclib.ifcs              import SendIfcRTL
from directions              import *
from MeshRouterFL            import MeshRouterFL
from ocn_pclib.ifcs.Packet   import *
from ocn_pclib.ifcs.Position import *

class MeshNetworkFL( Component ):
  def construct( s, PacketType, PositionType, mesh_wid = 4, mesh_ht = 4 ):

    # Constants

    s.num_routers = mesh_wid * mesh_ht
    s.num_terminals = s.num_routers

    # Interface

    s.recv = [ RecvIfcRTL(PacketType) for _ in range( s.num_terminals ) ]
    s.send = [ SendIfcRTL(PacketType) for _ in range( s.num_terminals ) ]

    # Components

    s.routers  = [ MeshRouterFL( PacketType, PositionType, 5, 5 )
                 for i in range( s.num_routers ) ]

    # Connect s.routers together in Mesh

    for i in range( s.num_routers ):
      if i / mesh_wid > 0:
        s.connect( s.routers[i].send[SOUTH], s.routers[i-mesh_wid].recv[NORTH] )

      if i / mesh_wid < mesh_ht - 1:
        s.connect( s.routers[i].send[NORTH], s.routers[i+mesh_wid].recv[SOUTH] )

      if i % mesh_wid > 0:
        s.connect( s.routers[i].send[WEST], s.routers[i-1].recv[EAST] )

      if i % mesh_wid < mesh_wid - 1:
        s.connect( s.routers[i].send[EAST], s.routers[i+1].recv[WEST] )

      # Connect the self port (with Network Interface)

      s.connect(s.recv[i], s.routers[i].recv[SELF])
      s.connect(s.send[i], s.routers[i].send[SELF])

      # Connect the unused ports

#      if i / mesh_wid == 0:
#        s.connect( s.routers[i].send[SOUTH].rdy,         0 )
#        s.connect( s.routers[i].recv[SOUTH].en,          0 )
#        s.connect( s.routers[i].recv[SOUTH].msg.payload, 0 )
#
#      if i / mesh_wid == mesh_ht - 1:
#        s.connect( s.routers[i].send[NORTH].rdy,         0 )
#        s.connect( s.routers[i].recv[NORTH].en,          0 )
#        s.connect( s.routers[i].recv[NORTH].msg.payload, 0 )
#
#      if i % mesh_wid == 0:
#        s.connect( s.routers[i].send[WEST].rdy,          0 )
#        s.connect( s.routers[i].recv[WEST].en,           0 )
#        s.connect( s.routers[i].recv[WEST].msg.payload,  0 )
#
#      if i % mesh_wid == mesh_wid - 1:
#        s.connect( s.routers[i].send[EAST].rdy,          0 )
#        s.connect( s.routers[i].recv[EAST].en,           0 )
#        s.connect( s.routers[i].recv[EAST].msg.payload,  0 )

    # FIXME: unable to connect a struct to a port.
    @s.update
    def up_pos():
      for y in range( mesh_ht ):
        for x in range( mesh_wid ):
          idx = y * mesh_wid + x
          s.routers[idx].pos = PositionType( x, y )

  def line_trace( s ):
    trace = [ "" for _ in range( s.num_terminals ) ]
    for i in range( s.num_terminals ):
      trace[i] += s.send[i].line_trace()
    return "|".join( trace )
