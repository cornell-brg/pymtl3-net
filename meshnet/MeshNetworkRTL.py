"""
=========================================================================
MeshNetworkRTL.py
=========================================================================
Mesh network implementation.

Author : Cheng Tan
  Date : Mar 10, 2019
"""
from pymtl3                         import *
from .directions                    import *
from channel.ChannelRTL             import ChannelRTL
from .MeshRouterRTL                 import MeshRouterRTL
from pymtl3.stdlib.ifcs.SendRecvIfc import *

class MeshNetworkRTL( Component ):
  def construct( s, PacketType, PositionType,
                 mesh_wid = 4, mesh_ht = 4, chl_lat = 0 ):

    # Constants

    s.num_routers   = mesh_wid * mesh_ht
    s.num_terminals = s.num_routers
    num_channels    = (mesh_ht*(mesh_wid-1)+mesh_wid*(mesh_ht-1)) * 2
    chl_lat         =  0

    # Interface

    s.recv = [ RecvIfcRTL( PacketType ) for _ in range( s.num_terminals )]
    s.send = [ SendIfcRTL( PacketType ) for _ in range( s.num_terminals )]

    # Components

    s.routers  = [ MeshRouterRTL( PacketType, PositionType )
                 for i in range( s.num_routers ) ]

    s.channels = [ ChannelRTL( PacketType, latency = chl_lat )
                 for _ in range( num_channels ) ]

    XYType  = mk_bits( clog2( mesh_wid ) )
    s.pos_x = [ InPort(XYType) for _ in range( s.num_routers )]
    s.pos_y = [ InPort(XYType) for _ in range( s.num_routers )]

    for r in range( s.num_routers ):
      s.pos_x[r] //= s.routers[r].pos.pos_x
      s.pos_y[r] //= s.routers[r].pos.pos_y


    # Connect routers together in Mesh

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

      s.recv[i] //= s.routers[i].recv[SELF]
      s.send[i] //= s.routers[i].send[SELF]

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
        s.routers[i].send[WEST].rdy          //= 0
        s.routers[i].recv[WEST].en           //= 0
        s.routers[i].recv[WEST].msg.payload  //= 0

      if i % mesh_wid == mesh_wid - 1:
        s.routers[i].send[EAST].rdy          //= 0
        s.routers[i].recv[EAST].en           //= 0
        s.routers[i].recv[EAST].msg.payload  //= 0

  def line_trace( s ):
    trace = "|".join([ str(s.send[i]) for i in range( s.num_terminals ) ])
    return trace
