'''
==========================================================================
MeshWrapper.py
==========================================================================
Add a dummy node for each router.

Author: Yanghui Ou
Date  : July 22, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL

from ocnlib.rtl.DummyCore import DummyCore

from ..MeshNetworkMflitRTL import MeshNetworkMflitRTL


class MeshWrapper( Component ):

  def construct( s, Header, Position, ncols=2, nrows=2 ):

    # Local parameters

    s.ntiles   = ncols * nrows
    s.PhitType = mk_bits( Header.nbits )

    # Interface

    s.recv = [ RecvIfcRTL( s.PhitType ) for _ in range( s.ntiles ) ]
    s.send = [ SendIfcRTL( s.PhitType ) for _ in range( s.ntiles ) ]

    # Component

    s.cores = [ DummyCore( Header ) for _ in range( s.ntiles ) ]
    s.net   = MeshNetworkMflitRTL( Header, Position, ncols, nrows )

    # Connection

    for i in range( s.ntiles ):
      s.recv[i] //= s.cores[i].recv
      s.send[i] //= s.cores[i].send
      s.cores[i].net_send //= s.net.recv[i]
      s.cores[i].net_recv //= s.net.send[i]

  def line_trace( s ):
    return s.net.line_trace()

