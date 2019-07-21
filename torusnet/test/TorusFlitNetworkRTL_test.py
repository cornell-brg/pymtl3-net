#=========================================================================
# TorusFlitNetworkRTL_test.py
#=========================================================================
# Test for flit-based TorusNetworkRTL
#
# Author : Cheng Tan
#   Date : July 21, 2019

import hypothesis
from hypothesis                         import strategies as st
from pymtl3                             import *
from pymtl3.stdlib.test.test_srcs       import TestSrcRTL
from ocn_pclib.test.net_sinks           import TestNetSinkRTL
from ocn_pclib.ifcs.flits               import *
from ocn_pclib.ifcs.packets             import mk_mesh_pkt
from ocn_pclib.ifcs.positions           import mk_mesh_pos
from torusnet.TorusFlitNetworkRTL       import TorusFlitNetworkRTL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, PktType, ncols, nrows, src_msgs, sink_msgs ):

    s.nrouters = ncols * nrows
    MeshPos = mk_mesh_pos( ncols, nrows )
    match_func = lambda a, b : a.payload == b.payload

    s.srcs  = [ TestSrcRTL   ( PktType, src_msgs[i] )
                for i in range ( s.nrouters ) ]
    s.dut   = TorusFlitNetworkRTL( PktType, MeshPos, ncols, nrows, 0)
    s.sinks = [ TestNetSinkRTL  ( PktType, sink_msgs[i], match_func=match_func )
                for i in range ( s.nrouters ) ]

    # Connections
    for i in range ( s.nrouters ):
      s.connect( s.srcs[i].send, s.dut.recv[i]   )
      s.connect( s.dut.send[i],  s.sinks[i].recv )

  def done( s ):
    srcs_done  = True
    sinks_done = True
    for i in range( s.nrouters ):
      if not s.srcs[i].done():
        srcs_done = False
        break
      if not s.sinks[i].done():
        sinks_done = False
        break
    return srcs_done and sinks_done

  def line_trace( s ):
    return s.dut.line_trace()

#=========================================================================
# Test cases
#=========================================================================

class TorusNetwork_Tests( object ):

  def run_sim( s, th, max_cycles=200 ):
    th.elaborate()
    th.apply( SimulationPass )
    th.sim_reset()

    # Run simulation
    ncycles = 0
    print ""
    print "{:3}:{}".format( ncycles, th.line_trace() )
    while not th.done() and ncycles < max_cycles:
      th.tick()
      ncycles += 1
      print "{:3}:{}".format( ncycles, th.line_trace() )

    # Check timeout
    assert ncycles < max_cycles

  def test_simple_flit( s ):

    ncols = 2
    nrows = 2
    opaque_nbits = 1
    nvcs = 2
    payload_nbits = 32
    flit_size = 16

    PktType  = mk_mesh_pkt ( ncols, nrows, opaque_nbits, 
                             nvcs, payload_nbits )
    FlitType = mk_mesh_flit( ncols, nrows, 0, opaque_nbits,
                             nvcs, flit_size )
    #           src_x  y dst_x y opq vc  payload
    pkt0 = PktType( 1, 0,   0, 1, 0,  0, 0xfaceb00c )
    pkt1 = PktType( 1, 1,   1, 0, 0,  0, 0xdeadface )
    flits0 = flitisize_mesh_flit( pkt0, ncols, nrows,
             opaque_nbits, nvcs, payload_nbits, flit_size )
    flits1 = flitisize_mesh_flit( pkt1, ncols, nrows,
             opaque_nbits, nvcs, payload_nbits, flit_size )
    src_flits = [ [], flits0, [], flits1 ]
    dst_flits = [ [], flits1, flits0, [] ]
    th = TestHarness( FlitType, ncols, nrows, src_flits, dst_flits )

    s.run_sim( th )
