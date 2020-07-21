#=========================================================================
# DORYRouteUnitRTL_test.py
#=========================================================================
# Test for DORYRouteUnitRTL
#
# Author : Yanghui Ou, Cheng Tan
#   Date : Mar 25, 2019

from pymtl3 import *
from pymtl3.stdlib.test_utils import TestVectorSimulator
from pymtl3.stdlib.test_utils.test_sinks import TestSinkRTL
from pymtl3.stdlib.test_utils.test_srcs import TestSrcRTL

from ocnlib.ifcs.packets import mk_mesh_pkt
from ocnlib.ifcs.positions import mk_mesh_pos
from ocnlib.utils import run_sim
from meshnet.DORYMeshRouteUnitRTL import DORYMeshRouteUnitRTL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, MsgType, src_msgs, sink_msgs, src_initial,
                 src_interval, sink_initial, sink_interval,
                 arrival_time=None ):

    ncols = 4
    nrows = 4

    MeshPos = mk_mesh_pos( ncols, nrows )
    s.dut = DORYMeshRouteUnitRTL( MsgType, MeshPos )
    s.dut.pos = MeshPos( 1, 1 )

    s.src   = TestSrcRTL   ( MsgType, src_msgs,  src_initial,  src_interval  )
    s.sinks = [ TestSinkRTL  ( MsgType, sink_msgs[i], sink_initial, sink_interval, arrival_time[i] )
                for i in range ( s.dut.num_outports ) ]

    # Connections
    s.src.send.msg //= s.dut.get.ret

    for i in range ( s.dut.num_outports ):
      s.dut.give[i].ret //= s.sinks[i].recv.msg

    @update
    def up_give_en():
      for i in range (s.dut.num_outports):
        both_rdy = s.dut.give[i].rdy & s.sinks[i].recv.rdy
        s.dut.give[i].en @= both_rdy
        s.sinks[i].recv.en @= both_rdy

    # FIXME: connect send to get
    # s.connect( s.src.send.rdy, Bits1( 1 )    )
    # s.connect( s.dut.get.rdy,  s.src.send.en )

  def done( s ):
    sinks_done = 1
    for i in range( s.dut.num_outports ):
      if s.sinks[i].done() == 0:
        sinks_done = 0
    return s.src.done() and sinks_done

  def line_trace( s ):
    return s.src.line_trace() + "-> | " + s.dut.line_trace() + \
                               " | -> " + s.sinks[0].line_trace()

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

#               x,y,pl,dir
test_msgs   = [(0,0,101,0), (0,2,102,1), (0,1,103,2), (2,1,104,3),
               (1,1,105,4), (1,1,106,4)]
result_msgs = [ [], [], [], [], [] ]

arrival_time = [ [1], [2], [3], [4], [5,6] ]

# def test_normal_simple():
#
#   src_packets = []
#   for ( dst_x, dst_y, payload, dir_out ) in test_msgs:
#     pkt = mk_pkt (0, 0, dst_x, dst_y, 1, payload)
#     src_packets.append( pkt )
#     result_msgs[dir_out].append ( pkt )
#
#   th = TestHarness( Packet, src_packets, result_msgs, 0, 0, 0, 0,
#                     arrival_time )
#   run_sim( th )
