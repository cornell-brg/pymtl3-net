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

from src.router.RouteUnitRTL  import RouteUnitRTL
from src.router.RouterRTL     import RouterRTL
from src.router.RoutingDORY  import RoutingDORY
from src.ChannelUnitRTL          import ChannelUnitRTL
from ocn_pclib.Packet             import Packet
from ocn_pclib.Position           import *

from Configs import configure_network

class MeshNetworkRTL( RTLComponent ):
#  def construct( s, RouterType, RoutingStrategyType, TopologyType ):
  def construct( s ):

    # Constants
    configs = configure_network()

    NORTH = 0
    SOUTH = 1
    WEST  = 2
    EAST  = 3
    SELF  = 4

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

    num_channels = s.num_routers+s.rows*(s.cols-1)+s.cols*(s.rows-1)

    s.channels   = [ChannelUnitRTL(Packet, NormalQueueRTL, num_stages=0)
#            for _ in range(s.num_routers*s.cols*s.rows)]
            for _ in range(num_channels) ]

    for i in range( s.num_routers ):
      for j in range( s.num_inports):
        s.connect( s.outputs[i*s.num_inports+j],  s.routers[i].outs[j]   )
      s.connect( s.pos_ports[i], s.routers[i].pos )

    channel_index  = 0
    # recv/send_index
    rs_i = s.num_routers

    for i in range (s.num_routers):
      # Connect s.routers together in Mesh
      if s.routers[i].router_id / s.cols > 0:
        s.connect( s.routers[i].send[NORTH],
                s.channels[channel_index].recv )
        s.connect( s.channels[channel_index].send,
                s.routers[s.routers[i].router_id-s.cols].recv[SOUTH] )
        channel_index += 1

      if s.routers[i].router_id / s.cols < s.rows - 1:
        s.connect( s.routers[i].send[SOUTH],
                s.channels[channel_index].recv )
        s.connect( s.channels[channel_index].send,
                s.routers[s.routers[i].router_id+s.cols].recv[NORTH] )
        channel_index += 1

      if s.routers[i].router_id % s.cols > 0:
        s.connect( s.routers[i].send[WEST],
                s.channels[channel_index].recv )
        s.connect( s.channels[channel_index].send,
                s.routers[s.routers[i].router_id-1].recv[EAST] )
        channel_index += 1

      if s.routers[i].router_id % s.cols < s.cols - 1:
        s.connect( s.routers[i].send[EAST],
                s.channels[channel_index].recv )
        s.connect( s.channels[channel_index].send,
                s.routers[s.routers[i].router_id+1].recv[WEST] )
        channel_index += 1

      # Connect the self port (with Network Interface)
      s.connect(s.recv_noc_ifc[i], s.routers[i].recv[SELF])
      s.connect(s.send_noc_ifc[i], s.routers[i].send[SELF])

      # Connect the unused ports
      if s.routers[i].router_id / s.cols == 0:
        s.connect( s.routers[i].send[NORTH], s.send[rs_i] )
        s.connect( s.routers[i].recv[NORTH], s.recv[rs_i] )
        rs_i += 1

      if s.routers[i].router_id / s.cols == s.rows - 1:
        s.connect( s.routers[i].send[SOUTH], s.send[rs_i] )
        s.connect( s.routers[i].recv[SOUTH], s.recv[rs_i] )
        rs_i += 1

      if s.routers[i].router_id % s.cols == 0:
        s.connect( s.routers[i].send[WEST], s.send[rs_i] )
        s.connect( s.routers[i].recv[WEST], s.recv[rs_i] )
        rs_i += 1

      if s.routers[i].router_id % s.cols == s.cols - 1:
        s.connect( s.routers[i].send[EAST], s.send[rs_i] )
        s.connect( s.routers[i].recv[EAST], s.recv[rs_i] )
        rs_i += 1


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
    
