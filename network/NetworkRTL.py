#=========================================================================
# NetworkRTL.py
#=========================================================================
# Simple network implementation.
#
# Author : Cheng Tan
#   Date : Mar 10, 2019

from pymtl                        import *
from pclib.ifcs.EnRdyIfc          import InEnRdyIfc, OutEnRdyIfc
from pclib.rtl  import NormalQueueRTL

from network.router.RouteUnitRTL  import RouteUnitRTL
from network.router.RouterRTL     import RouterRTL
from network.routing.RoutingDORY  import RoutingDORY
from network.topology.Mesh        import *
from network.topology.Torus       import *
from network.LinkUnitRTL          import LinkUnitRTL
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

    s.PosType = MeshPosition
    s.rows     = configs.rows
    s.cols     = s.num_routers/s.rows

    # Interface
    s.recv = [InEnRdyIfc(Packet)  for _ in range(s.num_routers*4)]
    s.send = [OutEnRdyIfc(Packet) for _ in range(s.num_routers*4)]
    s.recv_noc_ifc = [InEnRdyIfc(Packet)  for _ in range(s.num_routers)]
    s.send_noc_ifc = [OutEnRdyIfc(Packet) for _ in range(s.num_routers)]

    # This outputs used to print the direction of the routing
    s.outputs = [ Wire( Bits3 )  for _ in range(s.num_routers*s.num_inports)]
    s.pos_ports = [ InVPort( s.PosType ) for _ in range(s.num_routers)]

    # Components
    s.routers = [RouterRTL(i, s.RoutingStrategyType, s.PosType, 
        QueueType=NormalQueueRTL) for i in range(s.num_routers)]

    s.links   = [LinkUnitRTL(Packet, NormalQueueRTL, num_stages=0)
#            for _ in range(s.num_routers*s.cols*s.rows)]
            for _ in range(s.num_routers+s.rows*(s.cols-1)+s.cols*(s.rows-1))]

#    mk_torus_topology(s)
    mk_mesh_topology(s)

    for i in range( s.num_routers ):
      for j in range( s.num_inports):
        s.connect( s.outputs[i*s.num_inports+j],  s.routers[i].outs[j]   )
      s.connect( s.pos_ports[i], s.routers[i].pos )


  def line_trace( s ):
    trace = ''
    for r in range(s.num_routers):
      trace += '\n({},{})|'.format(s.pos_ports[r].pos_x, s.pos_ports[r].pos_y)
      for i in range(s.num_inports):
        trace += '|{}:{}->({},{})'.format( i, 
                s.routers[r].recv[i].msg.payload, 
                s.routers[r].recv[i].msg.dst_x,
                s.routers[r].recv[i].msg.dst_y)
      trace += '\n out: '
      for i in range(s.num_outports):
        trace += '|{}:{}->({},{})'.format( i, 
                s.routers[r].send[i].msg.payload, 
                s.routers[r].send[i].msg.dst_x,
                s.routers[r].send[i].msg.dst_y)
    return trace
    
