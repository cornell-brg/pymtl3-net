"""
==========================================================================
CMeshNetworkRTL.py
==========================================================================
RTL implementation of concetrated mesh network.

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
                 ncols=4, nrows=4, num_nodes_each=4, chl_lat=0 ):

    # Constants

    s.num_routers   = ncols * nrows
    s.num_terminals = s.num_routers * num_nodes_each
    num_channels    = (nrows*(ncols-1)+ncols*(nrows-1)) * 2
    num_inports     = 4 + num_nodes_each
    num_outports    = 4 + num_nodes_each
    chl_lat         = 0
    XType           = mk_bits( clog2(ncols) )
    YType           = mk_bits( clog2(nrows ) )

    # Interface

    s.recv = [ RecvIfcRTL(PacketType) for _ in range( s.num_terminals ) ]
    s.send = [ SendIfcRTL(PacketType) for _ in range( s.num_terminals ) ]

    # Components

    s.routers  = [ CMeshRouterRTL( PacketType, PositionType, num_inports,
                     num_outports ) for i in range( s.num_routers ) ]

    s.channels = [ ChannelRTL( PacketType, latency = chl_lat)
                   for _ in range( num_channels ) ]

    # Connect s.routers together in Mesh
    # FIXME: we need to calculate the bit width for directions. Currently
    # the translation pass may throw an error.

    chl_id  = 0
    for i in range( s.num_routers ):
      if i // ncols > 0:
        s.routers[i].send[SOUTH] //= s.channels[chl_id].recv
        s.channels[chl_id].send  //= s.routers[i-ncols].recv[NORTH]
        chl_id += 1

      if i // ncols < nrows - 1:
        s.routers[i].send[NORTH] //= s.channels[chl_id].recv
        s.channels[chl_id].send  //= s.routers[i+ncols].recv[SOUTH]
        chl_id += 1

      if i % ncols > 0:
        s.routers[i].send[WEST] //= s.channels[chl_id].recv
        s.channels[chl_id].send //= s.routers[i-1].recv[EAST]
        chl_id += 1

      if i % ncols < ncols - 1:
        s.routers[i].send[EAST] //= s.channels[chl_id].recv
        s.channels[chl_id].send //= s.routers[i+1].recv[WEST]
        chl_id += 1

      # Connect the self port (with Network Interface)

      for j in range( num_nodes_each ):
        ifc_idx = i * num_nodes_each + j
        s.recv[ ifc_idx ] //= s.routers[ i ].recv[ 4 + j ]
        s.send[ ifc_idx ] //= s.routers[ i ].send[ 4 + j ]

      # Connect the unused ports

      if i // ncols == 0:
        s.routers[i].send[SOUTH].rdy         //= 0
        s.routers[i].recv[SOUTH].en          //= 0
        s.routers[i].recv[SOUTH].msg.payload //= 0

      if i // ncols == nrows - 1:
        s.routers[i].send[NORTH].rdy         //= 0
        s.routers[i].recv[NORTH].en          //= 0
        s.routers[i].recv[NORTH].msg.payload //= 0

      if i % ncols == 0:
        s.routers[i].send[WEST].rdy          //=  0
        s.routers[i].recv[WEST].en           //=  0
        s.routers[i].recv[WEST].msg.payload  //=  0

      if i % ncols == ncols - 1:
        s.routers[i].send[EAST].rdy          //=  0
        s.routers[i].recv[EAST].en           //=  0
        s.routers[i].recv[EAST].msg.payload  //=  0

#    # FIXME: unable to connect a struct to a port.
#    @s.update
#    def up_pos():
    for y in range( nrows ):
      for x in range( ncols ):
#        s.routers[y*ncols+x].pos = PositionType( x, y )
        s.routers[y*ncols+x].pos.pos_x //= XType(x)
        s.routers[y*ncols+x].pos.pos_y //= YType(y)

  def line_trace( s ):
    trace = [ f"{s.send[i]}" for i in range( s.num_terminals ) ]
    return "|".join( trace )
