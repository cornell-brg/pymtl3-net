#=========================================================================
# MeshNetworkRTL.py
#=========================================================================
# Mesh network implementation.
#
# Author : Cheng Tan
#   Date : Mar 10, 2019

from pymtl                   import *
from pclib.ifcs.SendRecvIfc  import *

from router.MeshRouterRTL    import MeshRouterRTL
from router.InputUnitRTL     import InputUnitRTL
from router.DORXRouteUnitRTL import DORXRouteUnitRTL
from router.DORYRouteUnitRTL import DORYRouteUnitRTL
from router.SwitchUnitRTL    import SwitchUnitRTL
from router.OutputUnitRTL    import OutputUnitRTL
from channel.ChannelUnitRTL  import ChannelUnitRTL

class MeshNetworkRTL( ComponentLevel6 ):
  def construct( s, PacketType, PositionType, mesh_wid=4, mesh_ht=4,
                 channel_latency=0, routing_dimension='y' ):

    # Constants

    NORTH = 0
    SOUTH = 1
    WEST  = 2
    EAST  = 3
    SELF  = 4

    s.num_routers     = mesh_wid * mesh_ht
    s.channel_latency = 0
    s.rows            = mesh_ht
    s.cols            = mesh_wid

    RouteUnitType = DORYRouteUnitRTL if routing_dimension=='y' else \
                    DORXRouteUnitRTL

    # number of interfaces that will not be used
    s.num_idleIfc = 4 * ((s.rows-2) * (s.cols-2) + 4)

    # Interface
    s.recv_idle  = [RecvIfcRTL(PacketType)  for _ in range(s.num_idleIfc)]
    s.send_idle  = [SendIfcRTL(PacketType)  for _ in range(s.num_idleIfc)] 
    s.recv       = [ RecvIfcRTL(PacketType) for _ in range(s.num_routers)]
    s.send       = [ SendIfcRTL(PacketType) for _ in range(s.num_routers)]

    # Components
    s.routers = [ MeshRouterRTL( PacketType, PositionType, RouteUnitType ) 
                  for i in range(s.num_routers)]

    num_channels = 2 * (s.rows*(s.cols-1)+s.cols*(s.rows-1))

    s.channels   = [ChannelUnitRTL(PacketType, latency=channel_latency)
            for _ in range( num_channels ) ]

    channel_index  = 0
    # recv/send_idle_index
    rs_i = s.num_routers

    for i in range (s.num_routers):
      # Connect s.routers together in Mesh
      if i / s.cols > 0:
        s.connect( s.routers[i].send[NORTH], s.channels[channel_index].recv )
        s.connect( s.channels[channel_index].send, s.routers[i-s.cols].recv[SOUTH] )
        channel_index += 1

      if i / s.cols < s.rows - 1:
        s.connect( s.routers[i].send[SOUTH], s.channels[channel_index].recv )
        s.connect( s.channels[channel_index].send, s.routers[i+s.cols].recv[NORTH] )
        channel_index += 1

      if i % s.cols > 0:
        s.connect( s.routers[i].send[WEST], s.channels[channel_index].recv )
        s.connect( s.channels[channel_index].send, s.routers[i-1].recv[EAST] )
        channel_index += 1

      if i % s.cols < s.cols - 1:
        s.connect( s.routers[i].send[EAST], s.channels[channel_index].recv )
        s.connect( s.channels[channel_index].send, s.routers[i+1].recv[WEST] )
        channel_index += 1

      # Connect the self port (with Network Interface)
      s.connect(s.recv[i], s.routers[i].recv[SELF])
      s.connect(s.send[i], s.routers[i].send[SELF])

      # Connect the unused ports
      if i / s.cols == 0:
        s.connect( s.routers[i].send[NORTH], s.send_idle[rs_i] )
        s.connect( s.routers[i].recv[NORTH], s.recv_idle[rs_i] )
        rs_i += 1

      if i / s.cols == s.rows - 1:
        s.connect( s.routers[i].send[SOUTH], s.send_idle[rs_i] )
        s.connect( s.routers[i].recv[SOUTH], s.recv_idle[rs_i] )
        rs_i += 1

      if i % s.cols == 0:
        s.connect( s.routers[i].send[WEST],  s.send_idle[rs_i] )
        s.connect( s.routers[i].recv[WEST],  s.recv_idle[rs_i] )
        rs_i += 1

      if i % s.cols == s.cols - 1:
        s.connect( s.routers[i].send[EAST],  s.send_idle[rs_i] )
        s.connect( s.routers[i].recv[EAST],  s.recv_idle[rs_i] )
        rs_i += 1

    @s.update
    def up_pos():
      for y in range( s.rows ):
        for x in range( s.cols ):
          idx = y * s.cols + x
          s.routers[idx].pos = PositionType( x, y )

  def line_trace( s ):
    trace = ''
    for r in range(s.num_routers):
      trace += '\n({},{})|'.format(s.routers[r].pos.pos_x, s.routers[r].pos.pos_y)
      for i in range(s.routers[r].num_inports):
        if isinstance(s.routers[r].recv[i].msg, int):
          trace += '|{}'.format(s.routers[r].recv[i].msg)
        else:
          trace += '|{}:{}->({},{})'.format( i, 
                s.routers[r].recv[i].msg.payload, 
                s.routers[r].recv[i].msg.dst_x,
                s.routers[r].recv[i].msg.dst_y)
      trace += '\n out: '
      for i in range(s.routers[r].num_outports):
        if isinstance(s.routers[r].send[i].msg, int):
          trace += '|{}'.format(s.routers[r].send[i].msg)
        else:
          trace += '|{}:{}->({},{})'.format( i, 
                s.routers[r].send[i].msg.payload, 
                s.routers[r].send[i].msg.dst_x,
                s.routers[r].send[i].msg.dst_y)
    return trace
    
