#=========================================================================
# RouterCharact_test.py
#=========================================================================
# Used for characterizaing router
#
# Author : Cheng Tan
#   Date : June 16, 2019

from pymtl3                         import *
from pymtl3.stdlib.test.test_srcs   import TestSrcRTL
from ocn_pclib.test.net_sinks       import TestNetSinkRTL
from ocn_pclib.ifcs.positions       import mk_mesh_pos
from ocn_pclib.ifcs.packets         import mk_cmesh_pkt
from pymtl3.stdlib.test             import TestVectorSimulator
from cmeshnet.CMeshRouterRTL        import CMeshRouterRTL
from cmeshnet.DORYCMeshRouteUnitRTL import DORYCMeshRouteUnitRTL
from router.InputUnitRTL            import InputUnitRTL
from router.OutputUnitRTL           import OutputUnitRTL
from router.SwitchUnitRTL           import SwitchUnitRTL

from test_helpers import dor_routing

from pymtl3.passes          import DynamicSim
from pymtl3.passes.sverilog import ImportPass, TranslationPass

import random

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, 
                 MsgType       = None, 
                 mesh_wid      = 2, 
                 mesh_ht       = 2, 
                 inports       = 8,
                 outports      = 8,
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
    s.dut = CMeshRouterRTL( MsgType, MeshPos, inports, outports, 
                            InputUnitType = InputUnitRTL, 
                            RouteUnitType = DORYCMeshRouteUnitRTL )

    s.srcs  = [ TestSrcRTL    ( MsgType, src_msgs[i],  src_initial,  src_interval  )
                for i in range  ( s.dut.num_inports ) ]
    s.sinks = [ TestNetSinkRTL( MsgType, sink_msgs[i], sink_initial, 
                sink_interval ) for i in range ( s.dut.num_outports ) ]

    # Connections

    for i in range ( s.dut.num_outports ):
      s.connect( s.srcs[i].send, s.dut.recv[i]   )
      s.connect( s.dut.send[i],  s.sinks[i].recv )

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

def run_sim( test_harness, max_cycles=100 ):

  # Create a simulator
  test_harness.elaborate()
  test_harness.dut.sverilog_translate = True
  test_harness.dut.sverilog_import = True
  test_harness.apply( TranslationPass() )
  test_harness = ImportPass()( test_harness )
#  test_harness.apply( SimpleSim )
  test_harness.apply( DynamicSim )
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

#  assert ncycles < max_cycles

  test_harness.tick()
  test_harness.tick()
  test_harness.tick()

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

def test_random():
  pos_x = 1
  pos_y = 1
  mesh_wid = 4
  mesh_ht  = 4
  inports  = 8
  outports = 8
  payload_wid = 8
  src_pkts  = [[] for _ in range(inports)]
  sink_pkts = [[] for _ in range(outports)]
  PacketType = mk_cmesh_pkt( mesh_wid, mesh_ht, inports, outports, 
                             payload_nbits=payload_wid )
  for _ in range(500):
    src_x = random.randint( 0, mesh_wid - 1 )
    src_y = random.randint( 0, mesh_ht  - 1 )
    dst_x = random.randint( 0, mesh_wid - 1 )
    dst_y = random.randint( 0, mesh_ht  - 1 )
    dst_t = random.randint( 0, outports - 5 )
    payload = random.randint( 0, 2**payload_wid )
    pkt = PacketType( src_x, src_y, dst_x, dst_y, dst_t, 0, payload)

    # Specific for DOR-Y routing
    # Set source port
    if src_y > pos_y:
      src_pkts[0].append( pkt )
    elif src_y < pos_y:
      src_pkts[1].append( pkt )
    elif src_x < pos_x:
      src_pkts[2].append( pkt )
    elif src_x > pos_x:
      src_pkts[3].append( pkt )
    else:
      src_pkts[4+dst_t].append( pkt )

    # Set destination port
    if dst_y > pos_y:
      sink_pkts[0].append( pkt )
    elif dst_y < pos_y:
      sink_pkts[1].append( pkt )
    else:
      if dst_x < pos_x:
        sink_pkts[2].append( pkt )
      elif dst_x > pos_x:
        sink_pkts[3].append( pkt )
      else:
        sink_pkts[4+dst_t].append( pkt )

  th = TestHarness( 
    PacketType, mesh_wid, mesh_ht, 
    inports, outports, 
    pos_x, pos_y,
    src_pkts, sink_pkts
  )
  run_sim( th )
