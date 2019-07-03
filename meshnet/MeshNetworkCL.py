#=========================================================================
# MeshNetworkCL.py
#=========================================================================
# Mesh network cycle level implementation.
#
# Author : Yanghui Ou
#   Date : May 21, 2019

from pymtl3            import *
from directions        import *
from channel.ChannelCL import ChannelCL
from MeshRouterCL      import MeshRouterCL

class MeshNetworkCL( Component ):
  def construct( s, PacketType, PositionType,
                 mesh_wid = 4, mesh_ht = 4, chl_lat = 0 ):

    # Constants

    s.num_routers = mesh_wid * mesh_ht
    s.num_terminals = s.num_routers
    num_channels  = (mesh_ht*(mesh_wid-1)+mesh_wid*(mesh_ht-1)) * 2
    chl_lat       =  0

    # Interface

    s.recv = [ NonBlockingCalleeIfc( PacketType ) for _ in range( s.num_terminals ) ]
    s.send = [ NonBlockingCallerIfc( PacketType ) for _ in range( s.num_terminals ) ]

    # Components

    s.routers  = [ MeshRouterCL( PacketType, PositionType )
                 for i in range( s.num_routers ) ]

    s.channels = [ ChannelCL( PacketType, latency = chl_lat)
                 for _ in range( num_channels ) ]

    # Connect s.routers together in Mesh

    chl_id  = 0
    for i in range( s.num_routers ):
      if i / mesh_wid > 0:
        s.connect( s.routers[i].send[SOUTH], s.channels[chl_id].recv )
        s.connect( s.channels[chl_id].send, s.routers[i-mesh_wid].recv[NORTH] )
        chl_id += 1

      if i / mesh_wid < mesh_ht - 1:
        s.connect( s.routers[i].send[NORTH], s.channels[chl_id].recv )
        s.connect( s.channels[chl_id].send, s.routers[i+mesh_wid].recv[SOUTH] )
        chl_id += 1

      if i % mesh_wid > 0:
        s.connect( s.routers[i].send[WEST], s.channels[chl_id].recv )
        s.connect( s.channels[chl_id].send, s.routers[i-1].recv[EAST] )
        chl_id += 1

      if i % mesh_wid < mesh_wid - 1:
        s.connect( s.routers[i].send[EAST], s.channels[chl_id].recv )
        s.connect( s.channels[chl_id].send, s.routers[i+1].recv[WEST] )
        chl_id += 1

      # Connect the self port (with Network Interface)

      s.connect(s.recv[i], s.routers[i].recv[SELF])
      s.connect(s.send[i], s.routers[i].send[SELF])

      # Connect the unused ports
      def dummy_rdy():
        return lambda : False

      # FIXME: this doesn't work!
      if i / mesh_wid == 0:
        print i, SOUTH
        s.routers[i].send[SOUTH].rdy.method = dummy_rdy()

      if i / mesh_wid == mesh_ht - 1:
        print i, NORTH
        s.routers[i].send[NORTH].rdy.method = dummy_rdy()

      if i % mesh_wid == 0:
        print i, WEST
        s.routers[i].send[WEST].rdy.method = dummy_rdy()

      if i % mesh_wid == mesh_wid - 1:
        print i, EAST
        s.routers[i].send[EAST].rdy.method = dummy_rdy()

    # FIXME: unable to connect a struct to a port.
    @s.update
    def up_pos():
      for y in range( mesh_ht ):
        for x in range( mesh_wid ):
          idx = y * mesh_wid + x
          s.routers[idx].pos = PositionType( x, y )

  def line_trace( s ):
    return "|".join( [ s.routers[i].line_trace() for i in range(s.num_routers) ] )
