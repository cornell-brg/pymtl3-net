#=========================================================================
# TorusRouterRTL_test.py
#=========================================================================
# Test for TorusRouterRTL
#
# Author : Cheng Tan
#   Date : June 28, 2019

from pymtl3                         import *
from pymtl3.stdlib.test.test_srcs   import TestSrcRTL
from ocn_pclib.test.net_sinks       import TestNetSinkRTL
from ocn_pclib.ifcs.positions       import mk_mesh_pos
from ocn_pclib.ifcs.packets         import mk_mesh_pkt
from pymtl3.stdlib.test             import TestVectorSimulator
from torusnet.TorusRouterRTL        import TorusRouterRTL
from torusnet.DORYTorusRouteUnitRTL import DORYTorusRouteUnitRTL
from test_helpers                   import dor_routing
from pymtl3.passes.sverilog         import ImportPass, TranslationPass
from pymtl3.passes                  import DynamicSim
from ocn_pclib.ifcs.CreditIfc       import RecvRTL2CreditSendRTL, CreditRecvRTL2SendRTL
from pymtl3.stdlib.ifcs             import SendIfcRTL, RecvIfcRTL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, 
                 MsgType       = None, 
                 mesh_wid      = 2, 
                 mesh_ht       = 2 , 
                 pos_x         = 0,
                 pos_y         = 0,
                 src_msgs      = [], 
                 sink_msgs     = [], 
                 src_initial   = 0, 
                 src_interval  = 0, 
                 sink_initial  = 0, 
                 sink_interval = 0,
                 arrival_time  =[None, None, None, None, None]
               ):

    print "=" * 74
    # print "src:", src_msgs
    # print "sink:", sink_msgs
    MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )
    s.dut = TorusRouterRTL( MsgType, MeshPos )

    s.srcs  = [ TestSrcRTL    ( MsgType, src_msgs[i],  src_initial,  src_interval  )
                for i in range  ( s.dut.num_inports ) ]
    s.sinks = [ TestNetSinkRTL( MsgType, sink_msgs[i], sink_initial, 
                sink_interval ) for i in range ( s.dut.num_outports ) ]
    for ss in sink_msgs:
      for sss in ss:
        print 'see sink: ', sss
      print '---'

    s.recv_adapters = [ RecvRTL2CreditSendRTL( MsgType, nvcs=2 ) 
                      for _ in range( s.dut.num_inports  ) ]
    s.send_adapters = [ CreditRecvRTL2SendRTL( MsgType, nvcs=2 ) 
                      for _ in range( s.dut.num_outports ) ]

    s.recv = [ RecvIfcRTL(MsgType) for _ in range(s.dut.num_inports )]
    s.send = [ SendIfcRTL(MsgType) for _ in range(s.dut.num_outports)]

    # Connections

    for i in range ( s.dut.num_outports ):
#      s.connect( s.srcs[i].send, s.recv[i]   )
#      s.connect( s.send[i],  s.sinks[i].recv )

      s.connect( s.srcs[i].send,          s.recv_adapters[i].recv )
      s.connect( s.recv_adapters[i].send, s.dut.recv[i]           )

      s.connect( s.dut.send[i],           s.send_adapters[i].recv )
      s.connect( s.send_adapters[i].send, s.sinks[i].recv         )

    #TODO: provide pos for router... 
    @s.update
    def up_pos():
      s.dut.pos = MeshPos( pos_x, pos_y )

  def done( s ):
    srcs_done = 1
    sinks_done = 1
#    for i in range( s.dut.num_inports ):
#      if s.srcs[i].done() == 0:
    for x in s.srcs:
      if x.done() == 0:
        srcs_done = 0
#    for i in range( s.dut.num_outports ):
#      if s.sinks[i].done() == 0:
    for x in s.sinks:
      if x.done() == 0:
        sinks_done = 0
    return srcs_done and sinks_done

  def line_trace( s ):
    return "{}".format(
      s.dut.line_trace(),
      #'|'.join( [ s.sinks[i].line_trace() for i in range(5) ] ), 
    )

#-------------------------------------------------------------------------
# run_rtl_sim
#-------------------------------------------------------------------------

def run_sim( test_harness, max_cycles=1000 ):

  # Create a simulator
  test_harness.elaborate()
#  test_harness.dut.sverilog_translate = True
#  test_harness.dut.sverilog_import = True
#  test_harness.apply( TranslationPass() )
#  test_harness = ImportPass()( test_harness )
  test_harness.apply( SimpleSim )
#  test_harness.apply( DynamicSim )
  test_harness.sim_reset()

  # Run simulation

  ncycles = 0
  print ""
  print "{}:{}".format( ncycles, test_harness.line_trace() )
  while not test_harness.done() and ncycles < max_cycles:
    test_harness.tick()
    ncycles += 1
    print "{}:{}".format( ncycles, test_harness.line_trace() )

  # Check timeout

  assert ncycles < max_cycles

  test_harness.tick()
  test_harness.tick()
  test_harness.tick()

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

#              x,y,pl,dir
test_msgs = [[(0,0,11,1),(0,0,12,1),(0,1,13,2),(2,1,14,3),(0,0,15,1)],
             [(0,0,21,1),(0,2,22,0),(0,1,23,2),(2,1,24,3),(2,1,25,3)],
             [(0,2,31,0),(0,0,32,1),(0,1,33,2),(1,1,34,4),(1,1,35,4)]
            ]
result_msgs = [[],[],[],[],[]]

def ttest_normal_simple():

  src_packets = [[],[],[],[],[]]
  for item in test_msgs:
    for i in range( len( item ) ):
      (dst_x,dst_y,payload,dir_out) = item[i]
      PacketType = mk_mesh_pkt (4, 4)
      pkt = PacketType (0, 0, dst_x, dst_y, 1, payload)
      src_packets[i].append( pkt )
      result_msgs[dir_out].append( pkt )

  th = TestHarness( PacketType, 4, 4, 1, 1, src_packets, result_msgs, 0, 0, 0, 0 )
  run_sim( th )

def ttest_self_simple():
  PacketType = mk_mesh_pkt(4, 4)
  pkt = PacketType( 0, 0, 0, 0, 0, 0xdead )
  src_pkts  = [ [], [], [], [], [pkt] ]
  sink_pkts = [ [], [], [], [], [pkt] ]
  th = TestHarness( PacketType, 4, 4, 0, 0, src_pkts, sink_pkts )
  run_sim( th )

# Failing test cases captured by hypothesis
def test_h0():
  pos_x = 0
  pos_y = 0
  mesh_wid = 2
  mesh_ht  = 2
  PacketType = mk_mesh_pkt( mesh_wid, mesh_ht, nvcs=2 )
  pkt0 = PacketType( 0, 0, 1, 0, 0, 0, 0x0 )
  pkt1 = PacketType( 0, 1, 1, 0, 0, 0, 0x1 )
  pkt2 = PacketType( 0, 1, 1, 0, 0, 0, 0x2 )
  pkt3 = PacketType( 0, 1, 1, 0, 0, 0, 0x3 )
  pkt4 = PacketType( 0, 1, 1, 0, 0, 0, 0x4 )
  pkt5 = PacketType( 0, 1, 0, 1, 0, 0, 0x5 )
  pkt6 = PacketType( 0, 1, 0, 1, 0, 0, 0x6 )
  pkt7 = PacketType( 0, 1, 0, 0, 0, 0, 0x7 )
#  src_pkts  = [ [pkt1,pkt2,pkt3], [pkt5], [pkt6], [pkt7], [pkt0,pkt4] ]
#  sink_pkts = [ [pkt5,pkt6], [], [], [pkt0,pkt1,pkt2,pkt3,pkt4], [pkt7] ]
  src_pkts  = [ [], [pkt5], [], [pkt7], [pkt0] ]
  sink_pkts = [ [pkt5], [], [], [pkt0], [pkt7] ]
  th = TestHarness( 
    PacketType, mesh_wid, mesh_ht, pos_x, pos_y,
    src_pkts, sink_pkts
  )
  run_sim( th )

def ttest_h1():
  pos_x, pos_y, mesh_wid, mesh_ht = 0, 0, 2, 2 
  PacketType = mk_mesh_pkt( mesh_wid, mesh_ht )
  pkt0 = PacketType( 0, 0, 0, 1, 0, 0xdead )
  src_pkts  = [ [],     [], [], [], [pkt0] ]
  sink_pkts = [ [pkt0], [], [], [], []     ]
  th = TestHarness( 
    PacketType, mesh_wid, mesh_ht, pos_x, pos_y,
    src_pkts, sink_pkts
  )
  th.set_param( 
    "top.dut.construct", 
    RouteUnitType = DORYMeshRouteUnitRTL 
  )
  run_sim( th )

def ttest_h2():
  pos_x, pos_y, mesh_wid, mesh_ht = 0, 0, 2, 2 
  PacketType( mesh_wid, mesh_ht )
  pkt0 = PacketType( 0, 0, 1, 0, 0, 0xdead )
  pkt1 = PacketType( 0, 1, 1, 0, 1, 0xbeef )
  pkt2 = PacketType( 0, 1, 1, 0, 2, 0xcafe )
              # N             S   W   E                   self
  src_pkts  = [ [pkt1, pkt2], [], [], [],                 [pkt0] ]
  sink_pkts = [ [],           [], [], [pkt1, pkt2, pkt0], []     ]
  th = TestHarness( 
    PacketType, mesh_wid, mesh_ht, pos_x, pos_y,
    src_pkts, sink_pkts
  )
  th.set_param( 
    "top.dut.construct",
    RouteUnitType = DORYMeshRouteUnitRTL
  )
  run_sim( th, 10 )

def ttest_h3():
  pos_x, pos_y, mesh_wid, mesh_ht = 0, 1, 2, 2 
  PacketType = mk_mesh_pkt( mesh_wid, mesh_ht )
  pkt0 = PacketType( 0, 1, 0, 0, 0, 0xdead )
              # N   S   W   E   self
  src_pkts  = [ [], [], [], [], [pkt0] ]
  sink_pkts = [ [], [pkt0], [], [], [] ]
  th = TestHarness( 
    PacketType, mesh_wid, mesh_ht, pos_x, pos_y,
    src_pkts, sink_pkts
  )
  th.set_param( 
    "top.dut.construct", 
    RouteUnitType = DORYMeshRouteUnitRTL
  )
  run_sim( th, 10 )

