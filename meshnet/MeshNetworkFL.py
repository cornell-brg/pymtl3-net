"""
==========================================================================
MeshNetworkFL.py
==========================================================================
Functional level implementation of a mesh network.

Author : Yanghui Ou
  Date : July 6, 2019
"""
from pymtl3                  import *
from pymtl3.stdlib.ifcs      import RecvIfcRTL
from pymtl3.stdlib.ifcs      import SendIfcRTL
from collections import deque
from directions              import *

class MeshNetworkFL( Component ):
  def construct( s, PacketType, mesh_wid = 4, mesh_ht = 4 ):

    # Local Parameters
    s.mesh_wid   = mesh_wid
    s.mesh_ht    = mesh_ht
    s.ntermimals = mesh_wid * mesh_ht

    # Interface
    s.recv = [ NonBlockingCalleeIfc( PacketType )
               for _ in range( s.ntermimals ) ]
    s.give = [ NonBlockingCalleeIfc( PacketType )
               for _ in range( s.ntermimals ) ]

    # Components
    s.give_queue = [ deque() for _ in range( s.ntermimals  ) ]

    # Assign method to method ports
    for i in range( s.ntermimals ):
      s.give[i].method.method = s.give_queue[i].popleft
      s.recv[i].method.method = s.recv_

    for i in range( s.ntermimals ):
      s.recv[i].rdy.method    = lambda s: True
      s.give[i].rdy.method    = lambda s: len( s.give_queue[i] ) > 0

  def recv_( s, pkt ):
    dst_id = pkt.dst_x + pkt.dst_y * s.mesh_wid
    s.give_queue[ dst_id ].append( pkt )

  def line_trace( s ):
    in_trace  = [ str( s.recv ) for _ in range( s.ntermimals ) ]
    out_trace = [ str( s.give ) for _ in range( s.ntermimals ) ]
    return "{}_()_{}".join( "|".join( in_trace ), "|".join( out_trace ) )

class WrappedMeshNetFL( Component ):

  def construct( s, PacketType, mesh_wid = 4, mesh_ht = 4 ):

    # Local Parameters
    s.mesh_wid   = mesh_wid
    s.mesh_ht    = mesh_ht
    s.ntermimals = mesh_wid * mesh_ht

    s.recv = [ NonBlockingCalleeIfc( PacketType )
               for _ in range( s.ntermimals ) ]
    s.send = [ NonBlockingCallerIfc( PacketType )
               for _ in range( s.ntermimals ) ]

    s.net = MeshNetworkFL( PacketType, mesh_wid, mesh_ht )

    @s.update
    def up_give_send():
      for i in range( s.ntermimals ):
        if s.net.give[i].rdy() and s.send[i].rdy():
          s.send[i]( s.net.give[i]() )

  def line_trace( s ):
    return s.net.line_trace()