'''
==========================================================================
MeshNetworkMFlitRTL.py
==========================================================================
Mesh network that supports multi-flit packet.

Author : Yanghui Ou
  Date : Feb 13, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL

from .directions import *
from .MeshRouterMFlitRTL import MeshRouterMFlitRTL


class MeshNetworkMFlitRTL( Component ):

  #-----------------------------------------------------------------------
  # construct
  #-----------------------------------------------------------------------
  # TODO: parametrize channel latency.

  def construct( s, Header, PositionType, ncols=2, nrows=2 ):

    # Local parameters

    s.nterminals = ncols * nrows
    s.PhitType   = mk_bits( get_nbits( Header ) )

    # Interface

    s.recv = [ RecvIfcRTL( s.PhitType ) for _ in range( s.nterminals ) ]
    s.send = [ SendIfcRTL( s.PhitType ) for _ in range( s.nterminals ) ]

    # Components

    s.routers = [ MeshRouterMFlitRTL( Header, PositionType )
                  for _ in range( s.nterminals ) ]

    # Set position of each router

    for y in range( nrows ):
      for x in range( ncols ):
        s.routers[ y*ncols + x ].pos //= PositionType( x, y )

    # Connect routers

    for i in range( s.nterminals ):
      if i // ncols > 0:
        s.routers[i].send[SOUTH] //= s.routers[i-ncols].recv[NORTH]

      if i // ncols < nrows - 1:
        s.routers[i].send[NORTH] //= s.routers[i+ncols].recv[SOUTH]

      if i % ncols > 0:
        s.routers[i].send[WEST] //= s.routers[i-1].recv[EAST]

      if i % ncols < ncols - 1:
        s.routers[i].send[EAST] //= s.routers[i+1].recv[WEST]

      # Connect the self port (with Network Interface)

      s.recv[i] //= s.routers[i].recv[SELF]
      s.send[i] //= s.routers[i].send[SELF]

      # Connect the unused ports
      # FIXME: for now we hackily ground the payload field so that pymtl
      # won't complain about net need driver.

      if i // ncols == 0:
        s.routers[i].send[SOUTH].rdy //= 0
        s.routers[i].recv[SOUTH].en  //= 0
        s.routers[i].recv[SOUTH].msg //= 0

      if i // ncols == nrows - 1:
        s.routers[i].send[NORTH].rdy //= 0
        s.routers[i].recv[NORTH].en  //= 0
        s.routers[i].recv[NORTH].msg //= 0

      if i % ncols == 0:
        s.routers[i].send[WEST].rdy //= 0
        s.routers[i].recv[WEST].en  //= 0
        s.routers[i].recv[WEST].msg //= 0

      if i % ncols == ncols - 1:
        s.routers[i].send[EAST].rdy //= 0
        s.routers[i].recv[EAST].en  //= 0
        s.routers[i].recv[EAST].msg //= 0

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    in_trace  = '|'.join([ f'{ifc}' for ifc in s.recv ])
    out_trace = '|'.join([ f'{ifc}' for ifc in s.send ])
    return f'{in_trace}(){out_trace}'
