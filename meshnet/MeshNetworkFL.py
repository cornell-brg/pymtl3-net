#=========================================================================
# MeshNetworkFL.py
#=========================================================================
# Mesh network implementation in FL modeling (magic crossbar).
#
# Author : Cheng Tan
#   Date : Mar 20, 2019

from pymtl3                   import *
from pymtl3.stdlib.ifcs              import RecvIfcRTL
from pymtl3.stdlib.ifcs              import SendIfcRTL
from directions              import *
from ocn_pclib.ifcs.Packet   import *
from ocn_pclib.ifcs.Position import *

class MeshNetworkFL( Component ):
  def construct( s, PacketType, mesh_wid = 4, mesh_ht = 4 ):

    # Constants

    s.num_routers = mesh_wid * mesh_ht
    s.num_terminals = s.num_routers

    # Interface

    s.recv = [ RecvIfcRTL(PacketType) for _ in range( s.num_terminals ) ]
    s.send = [ SendIfcRTL(PacketType) for _ in range( s.num_terminals ) ]

    # Components

    s.send_queue = [ [] for _ in range( s.num_terminals ) ]

    @s.update
    def routing():
      for i in range( s.num_terminals ):
        if s.recv[i].rdy != 0:
          dst = s.recv[i].msg.dst_y * mesh_wid + s.recv[i].msg.dst_x
          s.send_queue[dst].append( s.recv[i].msg )

      # Clear up send[] each time
      for i in range( s.num_terminals ):
        s.send[i].msg = None

      for i in range( s.num_terminals ):
        if len( s.send_queue[i] ) != 0:
          s.send[i].msg = s.send_queue[i].pop( 0 )

  def line_trace( s ):
    trace = [ "" for _ in range( s.num_terminals ) ]
    for i in range( s.num_terminals ):
      trace[i] += str(s.send[i].msg)
    return "|".join( trace )
