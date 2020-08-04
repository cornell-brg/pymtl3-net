'''
==========================================================================
MeshTile.py
==========================================================================
A tile module for mesh.

Author : Yanghui Ou
  Date : July 30, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL
from pymtl3.stdlib.basic_rtl import Reg

from ocnlib.rtl.DummyNode import DummyNode

from ..MeshRouterMflitRTL import MeshRouterMflitRTL

class MeshTile( Component ):

  def construct( s, Header, Position, ):

    # Local parameter
    
    s.PhitType = mk_bits( Header.nbits )

    # Interface

    s.recv = [ RecvIfcRTL( s.PhitType ) for _ in range(4) ]
    s.send = [ SendIfcRTL( s.PhitType ) for _ in range(4) ]
    s.pos  = InPort( Position )

    # Component

    s.core    = DummyNode( Header )
    s.router  = MeshRouterMflitRTL( Header, Position )
    s.pos_reg = Reg( Position )

    for i in range(4):
      s.recv[i] //= s.router.recv[i]
      s.send[i] //= s.router.send[i]

    s.pos //= s.pos_reg.in_
    s.pos_reg.out //= s.router.pos

    s.router.send[4] //= s.core.recv
    s.router.recv[4] //= s.core.send
  
  def line_trace( s ):
    return s.router.line_trace()
