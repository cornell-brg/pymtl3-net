'''
==========================================================================
MeshNetworkMflitRTL.py
==========================================================================
Mesh network that supports multi-flit packet.

Author : Yanghui Ou
  Date : Feb 13, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL

from channel.BidirectionalChannelRTL import BidirectionalChannelRTL as Channel

from .directions import *
from .MeshRouterMflitRTL import MeshRouterMflitRTL


class MeshNetworkMflitRTL( Component ):

  #-----------------------------------------------------------------------
  # construct
  #-----------------------------------------------------------------------
  # TODO: parametrize channel latency.

  def construct( s, Header, PositionType, ncols=2, nrows=2 ):

    # Local parameters

    s.nterminals   = ncols * nrows
    s.PhitType     = mk_bits( Header.nbits )
    s.num_channels = (nrows*(ncols-1)+ncols*(nrows-1)) * 2

    # s.num_sn_chnls = nrows * ( ncols - 1 )
    # s.num_we_chnls = ncols * ( nrows - 1 )
    s.num_sn_chnls = nrows * ( ncols )
    s.num_we_chnls = ncols * ( nrows )

    # Interface

    s.recv = [ RecvIfcRTL( s.PhitType ) for _ in range( s.nterminals ) ]
    s.send = [ SendIfcRTL( s.PhitType ) for _ in range( s.nterminals ) ]

    # Components

    s.routers = [ MeshRouterMflitRTL( Header, PositionType )
                  for _ in range( s.nterminals ) ]

    s.sn_chnls = [ Channel( s.PhitType ) for _ in range( s.num_sn_chnls ) ]
    s.we_chnls = [ Channel( s.PhitType ) for _ in range( s.num_we_chnls ) ]

    # Set position of each router

    for y in range( nrows ):
      for x in range( ncols ):
        s.routers[ y*ncols + x ].pos //= PositionType( x, y )

    # Connect routers and channels
    # For SN channels, use 0 for going north and 1 for going south
    # For WE channels, use 0 for going east and 1 for going west

    for i in range( s.nterminals ):

      # y > 0
      if i // ncols > 0:
        s.routers[i].send[SOUTH]    //= s.sn_chnls[i-ncols].recv[1]
        s.sn_chnls[i-ncols].send[1] //= s.routers[i-ncols].recv[NORTH]

      # y < nrows - 1
      if  i // ncols < nrows - 1:
        s.routers[i].send[NORTH] //= s.sn_chnls[i].recv[0]
        s.sn_chnls[i].send[0]    //= s.routers[i+ncols].recv[SOUTH]

      # x > 0
      if i % ncols > 0:
        s.routers[i].send[WEST] //= s.we_chnls[i-1].recv[1]
        s.we_chnls[i-1].send[1] //= s.routers[i-1].recv[EAST]

      # x <  ncols - 1
      if i % ncols < ncols - 1:
        s.routers[i].send[EAST] //= s.we_chnls[i].recv[0]
        s.we_chnls[i].send[0]   //= s.routers[i+1].recv[WEST]

      # Connect the self port (with Network Interface)

      s.recv[i] //= s.routers[i].recv[SELF]
      s.send[i] //= s.routers[i].send[SELF]

      # Connect the unused ports

      if i // ncols == 0:
        s.routers[i].send[SOUTH].rdy //= 0
        s.routers[i].recv[SOUTH].en  //= 0
        s.routers[i].recv[SOUTH].msg //= 0

      # Has dummy channel
      if i // ncols == nrows - 1:
        s.routers[i].send[NORTH]  //= s.sn_chnls[i].recv[0]
        s.sn_chnls[i].send[0].rdy //= 0

        s.routers[i].recv[NORTH]  //= s.sn_chnls[i].send[1]
        s.sn_chnls[i].recv[1].en  //= 0
        s.sn_chnls[i].recv[1].msg //= 0

      if i % ncols == 0:
        s.routers[i].send[WEST].rdy //= 0
        s.routers[i].recv[WEST].en  //= 0
        s.routers[i].recv[WEST].msg //= 0

      # Has dummy channel
      if i % ncols == ncols - 1:
        s.routers[i].send[EAST]   //= s.we_chnls[i].recv[0]
        s.we_chnls[i].send[0].rdy //= 0

        s.routers[i].recv[EAST]   //= s.we_chnls[i].send[1]
        s.we_chnls[i].recv[1].en  //= 0
        s.we_chnls[i].recv[1].msg //= 0

    # Connect routers - with no channels

    # for i in range( s.nterminals ):
    #   if i // ncols > 0:
    #     s.routers[i].send[SOUTH] //= s.routers[i-ncols].recv[NORTH]

    #   if i // ncols < nrows - 1:
    #     s.routers[i].send[NORTH] //= s.routers[i+ncols].recv[SOUTH]

    #   if i % ncols > 0:
    #     s.routers[i].send[WEST] //= s.routers[i-1].recv[EAST]

    #   if i % ncols < ncols - 1:
    #     s.routers[i].send[EAST] //= s.routers[i+1].recv[WEST]

    #   # Connect the self port (with Network Interface)

    #   s.recv[i] //= s.routers[i].recv[SELF]
    #   s.send[i] //= s.routers[i].send[SELF]

    #   # Connect the unused ports
    #   # FIXME: for now we hackily ground the payload field so that pymtl
    #   # won't complain about net need driver.

    #   if i // ncols == 0:
    #     s.routers[i].send[SOUTH].rdy //= 0
    #     s.routers[i].recv[SOUTH].en  //= 0
    #     s.routers[i].recv[SOUTH].msg //= 0

    #   if i // ncols == nrows - 1:
    #     s.routers[i].send[NORTH].rdy //= 0
    #     s.routers[i].recv[NORTH].en  //= 0
    #     s.routers[i].recv[NORTH].msg //= 0

    #   if i % ncols == 0:
    #     s.routers[i].send[WEST].rdy //= 0
    #     s.routers[i].recv[WEST].en  //= 0
    #     s.routers[i].recv[WEST].msg //= 0

    #   if i % ncols == ncols - 1:
    #     s.routers[i].send[EAST].rdy //= 0
    #     s.routers[i].recv[EAST].en  //= 0
    #     s.routers[i].recv[EAST].msg //= 0

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    in_trace  = '|'.join([ f'{ifc}' for ifc in s.recv ])
    out_trace = '|'.join([ f'{ifc}' for ifc in s.send ])
    return f'{in_trace}(){out_trace}'
