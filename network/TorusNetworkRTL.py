#=========================================================================
# NetworkRTL.py
#=========================================================================
# Simple network implementation.
#
# Author : Cheng Tan
#   Date : Mar 10, 2019

from pymtl                   import *
from pclib.ifcs.SendRecvIfc  import *
from ocn_pclib.ifcs.Packet   import Packet
from ocn_pclib.ifcs.Position import *

from router.RouterRTL        import RouterRTL
from router.InputUnitRTL     import InputUnitRTL
from router.DORXRouteUnitRTL import DORXRouteUnitRTL
from router.DORYRouteUnitRTL import DORYRouteUnitRTL
from router.SwitchUnitRTL    import SwitchUnitRTL
from router.OutputUnitRTL    import OutputUnitRTL
from channel.ChannelUnitRTL  import ChannelUnitRTL

from Configs import configure_network

class TorusNetworkRTL( RTLComponent ):
#  def construct( s, RouterType, RoutingStrategyType, TopologyType ):
  def construct( s ):

    # Constants
    configs = configure_network()

    NORTH = 0
    SOUTH = 1
    WEST  = 2
    EAST  = 3
    SELF  = 4

    s.num_inports     = configs.router_inports
    s.num_outports    = configs.router_outports
    s.num_routers     = configs.routers
    s.channel_latency = 0
    s.rows     = configs.rows
    s.cols     = s.num_routers/s.rows

    # Type for Mesh Network RTL
    s.PacketType     = Packet
    s.PositionType   = MeshPosition
    s.InputUnitType  = InputUnitRTL
    s.RouteUnitType  = DORYRouteUnitRTL
    s.SwitchUnitType = SwitchUnitRTL
    s.OutputUnitType = OutputUnitRTL

    # Interface
    s.recv = [RecvIfcRTL(s.PacketType)  for _ in range(s.num_routers*4)]
    s.send = [SendIfcRTL(s.PacketType) for _ in range(s.num_routers*4)]
    s.recv_noc_ifc = [RecvIfcRTL(s.PacketType)  for _ in range(s.num_routers)]
    s.send_noc_ifc = [SendIfcRTL(s.PacketType) for _ in range(s.num_routers)]

    # This outputs used to print the direction of the routing
    s.pos_ports = [ InVPort( s.PositionType ) for _ in range(s.num_routers)]

    # Components

    s.routers = [RouterRTL(s.PacketType, s.PositionType, s.num_inports,
        s.num_outports, s.InputUnitType, s.RouteUnitType, s.SwitchUnitType,
        s.OutputUnitType) for i in range(s.num_routers)]

    num_channels = 4*s.rows*s.cols

    s.channels   = [ChannelUnitRTL(PacketType=s.PacketType, latency=s.channel_latency)
            for _ in range(num_channels) ]

    for i in range( s.num_routers ):
      s.connect( s.pos_ports[i], s.routers[i].pos )

    channel_index  = 0
    # recv/send_index
    rs_i = s.num_routers

    for i in range (s.num_routers):
      # Connect s.routers together in Mesh
      s.connect(s.routers[i].send[NORTH], s.channels[channel_index].recv)
      s.connect(s.channels[channel_index].send, s.routers[(i-s.rows+
          s.num_routers)%s.num_routers].recv[SOUTH])
      channel_index += 1
 
      s.connect(s.routers[i].send[SOUTH], s.channels[channel_index].recv)
      s.connect(s.channels[channel_index].send, s.routers[(i+s.rows+
          s.num_routers)%s.num_routers].recv[NORTH])
      channel_index += 1
 
      s.connect(s.routers[i].send[WEST],  s.channels[channel_index].recv)
      s.connect(s.channels[channel_index].send, s.routers[(i-1+
           s.num_routers)%s.num_routers].recv[EAST])
      channel_index += 1
 
      s.connect(s.routers[i].send[EAST],  s.channels[channel_index].recv)
      s.connect(s.channels[channel_index].send, s.routers[(i+1+
          s.num_routers)%s.num_routers].recv[WEST])
      channel_index += 1

      # Connect the self port (with Network Interface)
      s.connect(s.recv_noc_ifc[i], s.routers[i].recv[SELF])
      s.connect(s.send_noc_ifc[i], s.routers[i].send[SELF])

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
    
