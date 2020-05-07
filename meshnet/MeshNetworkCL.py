#=========================================================================
# MeshNetworkCL.py
#=========================================================================
# Mesh network cycle level implementation.
#
# Author : Yanghui Ou
#   Date : May 21, 2019

from channel.ChannelCL import ChannelCL
from pymtl3 import *
from pymtl3.stdlib.cl.queues import BypassQueueCL
from ocnlib.cl import BoundaryUnit

from .directions import *
from .MeshRouterCL import MeshRouterCL


class MeshNetworkCL( Component ):
  def construct( s, PacketType, PositionType,
                 ncols = 4, nrows = 4, chl_lat = 0 ):

    # Constants

    s.num_routers = ncols * nrows
    s.num_terminals = s.num_routers
    num_channels  = (nrows*(ncols-1)+ncols*(nrows-1)) * 2
    chl_lat       =  0

    # Interface

    s.recv = [ CalleeIfcCL( Type=PacketType ) for _ in range( s.num_terminals ) ]
    s.send = [ CallerIfcCL( Type=PacketType ) for _ in range( s.num_terminals ) ]

    # Components

    s.routers  = [ MeshRouterCL( PacketType, PositionType )
                 for i in range( s.num_routers ) ]

    s.channels = [ ChannelCL( PacketType, latency = chl_lat)
                 for _ in range( num_channels ) ]

    # Connet unused port to dummy queues
    s.dangling_q_n = [ BoundaryUnit( default_rdy=False ) for _ in range( ncols ) ]
    s.dangling_q_s = [ BoundaryUnit( default_rdy=False ) for _ in range( ncols ) ]
    s.dangling_q_w = [ BoundaryUnit( default_rdy=False ) for _ in range( nrows ) ]
    s.dangling_q_e = [ BoundaryUnit( default_rdy=False ) for _ in range( nrows ) ]

    # Connect routers together in Mesh
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

      s.recv[i] //= s.routers[i].recv[SELF]
      s.send[i] //= s.routers[i].send[SELF]

      # Connect the unused ports to dummy methods
      # def dummy_rdy():
      #   return lambda : False

      # def dummy_method():
      #   ...

      # FIXME: this doesn't work!
      # if i // ncols == 0:
      #   s.routers[i].send[SOUTH].method.method = lambda s: None
      #   s.routers[i].send[SOUTH].rdy.method    = lambda s: False

      # if i // ncols == nrows - 1:
      #   s.routers[i].send[NORTH].method.method = lambda s: None
      #   s.routers[i].send[NORTH].rdy.method    = lambda s: False

      # if i % ncols == 0:
      #   s.routers[i].send[WEST].method.method = lambda s: None
      #   s.routers[i].send[WEST].rdy.method    = lambda s: False

      # if i % ncols == ncols - 1:
      #   s.routers[i].send[EAST].method.method = lambda s: None
      #   s.routers[i].send[EAST].rdy.method    = lambda s: False

      if i // ncols == 0:
        s.routers[i].send[ SOUTH ] //= s.dangling_q_s[ i % ncols ].recv

      if i // ncols == nrows - 1:
        s.routers[i].send[ NORTH ] //= s.dangling_q_n[ i % ncols ].recv

      if i % ncols == 0:
        s.routers[i].send[ WEST ] //= s.dangling_q_w[ i // ncols ].recv

      if i % ncols == ncols - 1:
        s.routers[i].send[ EAST ] //= s.dangling_q_e[ i // ncols ].recv

    # Set the position of each router
    for y in range( nrows ):
      for x in range( ncols ):
        idx = y * ncols + x
        s.routers[idx].pos //= PositionType( x, y )

  def line_trace( s ):
    return "|".join( [ s.routers[i].line_trace() for i in range(s.num_routers) ] )

#-------------------------------------------------------------------------
# WrappedMeshNetCL
#-------------------------------------------------------------------------
# A wrapped mesh net exposing only callee ports.

class WrappedMeshNetCL( Component ):

  def construct( s,
    PacketType,
    PositionType,
    ncols=4,
    nrows=4,
    chl_lat = 0
  ):
    s.nterminals = nrows * ncols
    s.recv = [ CalleeIfcCL( PacketType )  for _ in range( s.nterminals ) ]
    s.give = [ CalleeIfcCL( PacketType )  for _ in range( s.nterminals ) ]
    s.net = MeshNetworkCL( PacketType, PositionType, ncols, nrows, chl_lat )
    s.out_q = [ BypassQueueCL( num_entries=1 ) for _ in range( s.nterminals ) ]
    for i in range( s.nterminals ):
      s.recv[i]      //= s.net.recv[i]
      s.net.send[i]  //= s.out_q[i].enq
      s.out_q[i].deq //= s.give[i]

  def line_trace( s ):
    return s.net.line_trace()
