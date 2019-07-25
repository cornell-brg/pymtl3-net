"""
=========================================================================
CMeshNetworkRTL.py
=========================================================================
CMesh network implementation.

Author : Cheng Tan
  Date : Mar 10, 2019
"""
from pymtl3                         import *
from .directions                    import *
from .CMeshRouterRTL                import CMeshRouterRTL
from channel.ChannelRTL             import ChannelRTL
from pymtl3.stdlib.ifcs.SendRecvIfc import *

class CMeshNetworkRTL( Component ):
  def construct( s, PacketType, PositionType, 
                 mesh_wid = 4, mesh_ht = 4, num_nodes_each = 4, chl_lat = 0 ):

    # Constants

    s.num_routers   = mesh_wid * mesh_ht
    s.num_terminals = s.num_routers * num_nodes_each
    num_channels    = (mesh_ht*(mesh_wid-1)+mesh_wid*(mesh_ht-1)) * 2
    num_inports     = 4 + num_nodes_each
    num_outports    = 4 + num_nodes_each
    chl_lat         = 0

    # Interface

    s.recv = [ RecvIfcRTL(PacketType) for _ in range( s.num_terminals ) ]
    s.send = [ SendIfcRTL(PacketType) for _ in range( s.num_terminals ) ]

    # Components
    s.routers  = [ CMeshRouterRTL( PacketType, PositionType, num_inports, 
                 num_outports ) for i in range( s.num_routers ) ]

    s.channels = [ ChannelRTL( PacketType, latency = chl_lat)
                 for _ in range( num_channels ) ]

    # Connect s.routers together in Mesh

    chl_id  = 0
    for i in range( s.num_routers ):
      if i // mesh_wid > 0:
        s.routers[i].send[SOUTH] //= s.channels[chl_id].recv
        s.channels[chl_id].send  //= s.routers[i-mesh_wid].recv[NORTH]
        chl_id += 1

      if i // mesh_wid < mesh_ht - 1:
        s.routers[i].send[NORTH] //= s.channels[chl_id].recv
        s.channels[chl_id].send  //= s.routers[i+mesh_wid].recv[SOUTH]
        chl_id += 1

      if i % mesh_wid > 0:
        s.routers[i].send[WEST] //= s.channels[chl_id].recv
        s.channels[chl_id].send //= s.routers[i-1].recv[EAST]
        chl_id += 1

      if i % mesh_wid < mesh_wid - 1:
        s.routers[i].send[EAST] //= s.channels[chl_id].recv
        s.channels[chl_id].send //= s.routers[i+1].recv[WEST]
        chl_id += 1

      # Connect the self port (with Network Interface)
      
      for j in range( num_nodes_each ):
        s.recv[ i * num_nodes_each + j ] //=\
          s.routers[ i ].recv[ 4 + j ]
        s.send[ i * num_nodes_each + j ] //=\
                   s.routers[ i ].send[ 4 + j ]

      # Connect the unused ports

      if i // mesh_wid == 0:
        s.routers[i].send[SOUTH].rdy         //= 0
        s.routers[i].recv[SOUTH].en          //= 0
        s.routers[i].recv[SOUTH].msg.payload //= 0

      if i // mesh_wid == mesh_ht - 1:
        s.routers[i].send[NORTH].rdy         //= 0
        s.routers[i].recv[NORTH].en          //= 0
        s.routers[i].recv[NORTH].msg.payload //= 0

      if i % mesh_wid == 0:
        s.routers[i].send[WEST].rdy          //=  0
        s.routers[i].recv[WEST].en           //=  0
        s.routers[i].recv[WEST].msg.payload  //=  0

      if i % mesh_wid == mesh_wid - 1:
        s.routers[i].send[EAST].rdy          //=  0
        s.routers[i].recv[EAST].en           //=  0
        s.routers[i].recv[EAST].msg.payload  //=  0

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
