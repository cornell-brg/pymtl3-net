#=========================================================================
# NetworkRTL.py
#=========================================================================
# Simple network implementation.
#
# Author : Cheng Tan
#   Date : Mar 10, 2019

from pymtl                        import *
from pclib.ifcs.EnRdyIfc          import InEnRdyIfc, OutEnRdyIfc

from network.router.RouteUnitRTL  import RouteUnitRTL
from network.router.RouterRTL     import RouterRTL
from network.routing.RoutingDORY  import RoutingDORY
from network.topology.Mesh        import Mesh
from ocn_pclib.Packet             import Packet
from ocn_pclib.Position           import *

from Configs import configure_network

class NetworkRTL( RTLComponent ):
#  def construct( s, RouterType, RoutingStrategyType, TopologyType ):
  def construct( s ):

    configs = configure_network()

    s.num_outports = configs.router_outports
    s.num_inports  = configs.router_inports
    s.num_routers  = configs.routers
    s.RoutingStrategyType = RoutingDORY

    s.topology = Mesh()
    s.PositionType = MeshPosition
    s.num_rows     = configs.rows
    s.num_cols     = s.num_routers/s.num_rows
#    s.positions = mk_mesh_pos( configs.rows, s.num_routers)

    # Interface
    s.recv = [InEnRdyIfc(Packet)  for _ in range(s.num_routers*s.num_inports)]
    s.send = [OutEnRdyIfc(Packet) for _ in range(s.num_routers*s.num_outports)]
#+2*s.num_cols+2*s.num_rows)]

    s.outputs = [ Wire( Bits3 )  for _ in range( s.num_routers *  s.num_inports ) ]

    s.pos_ports = [ InVPort( s.PositionType ) for _ in range ( s.num_routers ) ]
#    s.pos = InVPort( s.PositionType )

    # Components
    s.routers = [ RouterRTL( i, s.RoutingStrategyType, s.PositionType ) 
                for i in range( s.num_routers ) ]

    # Connections
    for i in range(s.num_routers):
      s.connect(s.recv[i], s.routers[i].recv[4])
      s.connect(s.send[i], s.routers[i].send[4])
      print 'self router: ', i
#
#    for i in range(s.num_cols):
#      # North port connection
#      s.connect(s.send[i+s.num_routers], s.routers[i].send[0])
#      # South port connection
#      s.connect(s.send[s.num_routers+s.num_cols*2-i-1], 
#                s.routers[s.num_cols*s.num_rows-i-1].send[1])
#      print 'north router: ', i, '; and south router: ', s.num_cols*s.num_rows-i-1
#      print 'send: ', i+s.num_routers, '; and send: ', s.num_routers+s.num_cols*2-i-1
#
#    for i in range(s.num_rows):
#      # West port connection
#      s.connect(s.send[i+s.num_routers+s.num_cols*2], 
#                s.routers[i*s.num_cols].send[2])
#      # East port connection
#      s.connect(s.send[i+s.num_routers+s.num_cols*2+s.num_rows], 
#                s.routers[(i+1)*s.num_cols-1].send[3])
#      print 'west router: ', i*s.num_cols, '; and east router: ', (i+1)*s.num_cols-1
#      print 'send: ', i+s.num_routers+s.num_cols*2, '; and send: ', i+s.num_routers+s.num_cols*2+s.num_rows

    for i in range( s.num_routers ):
      for j in range( s.num_inports):
#        s.connect( s.recv[i * s.num_inports + j], s.routers[i].recv[j] )
        s.connect( s.outputs[i*s.num_inports+j],  s.routers[i].outs[j]   )
      s.connect( s.pos_ports[i], s.routers[i].pos )

#    for i in range( s.num_routers ):
#      for j in range( s.num_outports ):
#        s.connect( s.routers[i].send[j], s.send[i * s.num_outports + j] )
    
    s.topology.mk_topology( s, s.routers, s.num_rows )

  # TODO: Implement line trace.
  def line_trace( s ):
    return "pos:({},{}); src:({},{}); dst:({},{}); out_dir:({})".format(
s.pos_ports[3].pos_x, s.pos_ports[3].pos_y, s.recv[3].msg.src_x, s.recv[3].msg.src_y, 
s.recv[3].msg.dst_x, s.recv[3].msg.dst_y, s.outputs[15] )
    
