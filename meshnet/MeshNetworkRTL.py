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
                 mesh_wid=4, mesh_ht=4, chl_lat=0 ):

    # Local parameters

    s.num_routers   = mesh_wid * mesh_ht
    s.num_terminals = s.num_routers
    num_channels    = (mesh_ht*(mesh_wid-1)+mesh_wid*(mesh_ht-1)) * 2
    chl_lat         =  0
    XType           = mk_bits( clog2(mesh_wid) )
    YType           = mk_bits( clog2(mesh_ht ) )

    # Interface

    s.recv = [ RecvIfcRTL( PacketType ) for _ in range( s.num_terminals )]
    s.send = [ SendIfcRTL( PacketType ) for _ in range( s.num_terminals )]

    # Components

    s.routers  = [ MeshRouterRTL( PacketType, PositionType )
                   for i in range( s.num_routers ) ]

    s.channels = [ ChannelRTL( PacketType, latency = chl_lat )
                   for _ in range( num_channels ) ]

    # Wire the position ports of router

    for y in range( mesh_ht ):
      for x in range( mesh_wid ):
        s.routers[y*mesh_wid+x].pos.pos_x //= XType(x)
        s.routers[y*mesh_wid+x].pos.pos_y //= YType(y)

    # Connect routers together in Mesh
    # NOTE: for now we put all channels in a single list. In the future we
    # may want to divide channels into different groups so that it is
    # easier to configure.

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
      # FIXME: for now we hackily ground the payload field so that pymtl
      # won't complain about net need driver.

      if i // mesh_wid == 0:
        s.routers[i].send[SOUTH].rdy         //= b1(0)
        s.routers[i].recv[SOUTH].en          //= b1(0)
        s.routers[i].recv[SOUTH].msg.payload //= 0

      if i // mesh_wid == mesh_ht - 1:
        s.routers[i].send[NORTH].rdy         //= b1(0)
        s.routers[i].recv[NORTH].en          //= b1(0)
        s.routers[i].recv[NORTH].msg.payload //= 0

      if i % mesh_wid == 0:
        s.routers[i].send[WEST].rdy          //= b1(0)
        s.routers[i].recv[WEST].en           //= b1(0)
        s.routers[i].recv[WEST].msg.payload  //= 0

      if i % mesh_wid == mesh_wid - 1:
        s.routers[i].send[EAST].rdy          //= b1(0)
        s.routers[i].recv[EAST].en           //= b1(0)
        s.routers[i].recv[EAST].msg.payload  //= 0

  def line_trace( s ):
    trace = "|".join([ str(s.send[i]) for i in range( s.num_terminals ) ])
    return trace
