#!/usr/bin/env python
#=========================================================================
# netsim.py [options]
#=========================================================================
#
#  -h --help           Display this message
#  -v --verbose        Verbose mode
#
#  --impl <impl>       Choose model implementation
#                       fl   : functional level
#                       bus  : 4-terminal bus
#                       ring : 4-node ring
#
#  --pattern <pattern> Choose a network pattern
#                      urandom             dest = random % 4
#                      partition2          dest = (random & 2'b01) | (src & 2'b10)
#                      opposite            dest = (src + 2) % 4
#                      neighbor            dest = (src + 1) % 4
#                      complement          dest = ~src
#
#  --injection-rate    Injection rate of network message (in percent)
#  --sweep             Sweep the injection rates
#  --dump-vcd          Dump vcd
#  --stats             Print stats
#  --trace             Display line-trace
#
# The cache memory multiplier simulator. Choose an implementation and an
# access pattern to execute. Use --stats to display statistics about the
# simulation.
#
# Author : Cheng Tan
# Date   : April 14, 2018

#from __future__ import print_function

# Hack to add project root to python path

import os
import sys

sim_dir = os.path.dirname( os.path.abspath( __file__ ) )
os.system(sim_dir)
while sim_dir:
  if os.path.exists( sim_dir + os.path.sep + ".pymtl-python-path" ):
    sys.path.insert(0,sim_dir)
    # include the pymtl environment here
    sys.path.insert(0,sim_dir + "/../pymtl-v3/")
    break
  sim_dir = os.path.dirname(sim_dir)
  os.system(sim_dir)

import argparse
import re

from collections import deque
from random      import seed, randint

seed(0xdeadbeef)

from pymtl          import *

from meshnet.MeshNetworkRTL   import MeshNetworkRTL
from ringnet.RingNetworkRTL   import RingNetworkRTL
from torusnet.TorusNetworkRTL import TorusNetworkRTL
from bfnet    import BfNetworkRTL
from ocn_pclib.ifcs.Packet   import *
from ocn_pclib.ifcs.Position import *
from pclib.test import TestVectorSimulator

from pclib.test.test_srcs         import TestSrcRTL
from pclib.test.test_sinks        import TestSinkRTL
#-------------------------------------------------------------------------
# Command line processing
#-------------------------------------------------------------------------

class ArgumentParserWithCustomError(argparse.ArgumentParser):
  def error( s, msg = "" ):
    if ( msg ): print("\n ERROR: %s" % msg)
    print("")
    file = open( sys.argv[0] )
    for ( lineno, line ) in enumerate( file ):
      if ( line[0] != '#' ): sys.exit(msg != "")
      if ( (lineno == 2) or (lineno >= 4) ): print( line[1:].rstrip("\n") )

def parse_cmdline():
  parser = ArgumentParserWithCustomError( add_help=False )

  # Standard command line arguments

  parser.add_argument( "-v", 
                       "--verbose",  
                       action  = "store_true"                              )

  parser.add_argument( "-h", 
                       "--help",
                       action = "store_true"                               )

  parser.add_argument( "--pattern",  
                       choices = ["urandom", "partition2", "opposite", 
                                  "neighbor", "complement"], 
                       default = "urandom"                                 )

  parser.add_argument( "--injection-rate",              
                       type    = int, 
                       default = 10                                        )

  parser.add_argument( "--dump-vcd", 
                       action  = "store_true"                              )

  parser.add_argument( "--stats",    
                       action  = "store_true"                              )

  parser.add_argument( "--trace",  
                       action  = "store_true"                              )

  parser.add_argument( "--sweep",   
                       action  = "store_true"                              )

  # OCN related command line arguments

  parser.add_argument( "--topology",         
                       type    = str, 
                       default = "Mesh",
                       choices = [ 'Ring', 'Mesh', 'Torus', 'Bf' ],
                       help    = "topology can be applied in the network." )

  parser.add_argument( "--router-latency",   
                       type    = int, 
                       default = 1,
                       action  = "store",
                       help    = "number of pipeline stages in router."    )

  parser.add_argument( "--link-latency",     
                       type    = int, 
                       default = 1,
                       action  = "store",
                       help    = "number of input stages in router."       )

  parser.add_argument( "--link-width-bits",  
                       type    = int, 
                       default = 128,
                       action  = "store",
                       help    = "width in bits for all links."            )

  parser.add_argument( "--virtual-channel",  
                       type    = int, 
                       default = 4,
                       action  = "store",
                       help    = "number of virtual channels."             )

  parser.add_argument( "--routing-strategy", 
                       type    = str,
                       default = 'DORY',
                       action  = "store", 
                       choices = ['DORX', 'DORY', 'WFR', 'NLR'],
                       help    = "routing algorithm applied in network."   )

  parser.add_argument( "--routers",
                       type    = int, 
                       default = 16,
                       action  = "store",
                       help    = "number of routers in network."           )

  parser.add_argument( "--rows",
                       type    = int, 
                       default = 4,
                       action  = "store",
                       help    = "number of rows of routers in network."   )

  parser.add_argument( "--router-inports",   
                       type    = int, 
                       default = 5,
                       action  = "store",
                       help    = "number of inports in each router."       )

  parser.add_argument( "--router-outports",  
                       type    = int, 
                       default = 5,
                       action  = "store",
                       help    = "number of outports in each router."      )

  opts = parser.parse_args()
  if opts.help: parser.error()
  return opts

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, MsgType, mesh_wid, mesh_ht, src_msgs, sink_msgs,
                 src_initial, src_interval, sink_initial, sink_interval,
                 arrival_time=None ):

    MeshPos = mk_mesh_pos( mesh_wid, mesh_ht )
    s.dut = MeshNetworkRTL( MsgType, MeshPos, mesh_wid, mesh_ht, 0)

    s.srcs  = [ TestSrcRTL   ( MsgType, src_msgs[i],  src_initial,  src_interval  )
              for i in range ( s.dut.num_routers ) ]
    if arrival_time != None:
      s.sinks = [ TestSinkRTL  ( MsgType, sink_msgs[i], sink_initial,
                sink_interval, arrival_time[i]) for i in range ( s.dut.num_routers ) ]
    else:
      s.sinks = [ TestSinkRTL  ( MsgType, sink_msgs[i], sink_initial,
                sink_interval) for i in range ( s.dut.num_routers ) ]

    # Connections
    for i in range ( s.dut.num_routers ):
      s.connect( s.srcs[i].send, s.dut.recv[i]   )
      s.connect( s.dut.send[i],  s.sinks[i].recv )

  def done( s ):
    srcs_done = 1
    sinks_done = 1
    for i in range( s.dut.num_routers ):
      if s.srcs[i].done() == 0:
        srcs_done = 0
    for i in range( s.dut.num_routers ):
      if s.sinks[i].done() == 0:
        sinks_done = 0
    return srcs_done and sinks_done
  def line_trace( s ):
    return s.dut.line_trace()


#--------------------------------------------------------------------------
# Global Constants
#--------------------------------------------------------------------------

NUM_WARMUP_CYCLES   = 3000
NUM_SAMPLE_CYCLES   = 3000 + NUM_WARMUP_CYCLES
INVALID_TIMESTAMP   = 0

#--------------------------------------------------------------------------
# simulate
#--------------------------------------------------------------------------

def simulate( NetModel, num_nodes, net_width, net_height,
              injection_rate, pattern, drain_limit, dump_vcd, trace, verbose ):

  nports = num_nodes

  # Simulation Variables

  average_latency       = 0
  packets_generated     = 0
  packets_received      = 0
  all_packets_received  = 0
  total_latency         = 0
  drain_cycles          = 0
  sim_done              = False

  # Instantiate and elaborate a ring network
  
  MeshPos = mk_mesh_pos( net_width, net_height )
  
  model = NetModel( Packet, MeshPos, net_width, net_height, 0 )

  # Turn on vcd dumping

#  if dump_vcd:
#    model.vcd_file = dump_vcd
#    if hasattr(model, 'inner'):
#      model.inner.vcd_file = dump_vcd

  model.elaborate()

  # Source Queues - Modeled as Bypass Queues
  src_packets = [ [] for _ in range( num_nodes ) ]
  sink_packets = [ [] for _ in range( num_nodes ) ]

  test_msgs = [ (0, 15, 101), (1, 14, 102), (2, 13, 103), (3, 12, 104),
                (4, 11, 105), (5, 10, 106), (6,  9, 107), (7,  8, 108),
                (8,  7, 109), (9,  6, 110), (10, 5, 111), (11, 4, 112),
                (12, 3, 113), (13, 2, 114), (14, 1, 115), (15, 0, 116) ]

  arrival_pipes = None

  for (src, dst, payload) in test_msgs:
    pkt = mk_pkt( src%net_width, src/net_width, dst%net_width, 
                  dst/net_width, 1, payload )
    src_packets [src].append( pkt )
    sink_packets[dst].append( pkt )

  # Create a simulator 
  test_harness = TestHarness( Packet, net_width, net_height, 
                 src_packets, sink_packets, 0, 0, 0, 0, arrival_pipes )

  test_harness.apply( SimpleSim )

  # Reset the simulator

  test_harness.sim_reset()

  # Run simulation

  max_cycles = 10000
  ncycles = 0
  print ""
  print "{}:{}".format( ncycles, test_harness.line_trace() )
  while not test_harness.done() and ncycles < max_cycles:
    test_harness.tick()
    ncycles += 1
    print "{}:{}".format( ncycles, test_harness.line_trace() )

  # Check timeout

  assert ncycles < NUM_SAMPLE_CYCLES

  test_harness.tick()
  test_harness.tick()
  test_harness.tick()

#  # Run the simulation
#
#  for i in xrange(nports):
#    model.out[i].rdy.value = 1
#
#  while not sim_done:
#    # Iterate over all terminals
#    for i in xrange(nports):
#
#      # Generate packet
#
#      if ( randint( 1, 100 ) <= injection_rate ):
#
#        # traffic pattern based dest selection
#        if   pattern == "urandom":
#          dest = randint( 0, nports-1 )
#        elif pattern == "partition2":
#          dest = ( randint( 0, nports-1 ) ) & (nports/2-1) | ( i & (nports/2) )
#        elif pattern == "opposite":
#          dest = ( i + 2 ) % nports
#        elif pattern == "neighbor":
#          dest = ( i + 1 ) % nports
#        elif pattern == "complement":
#          dest = i ^ (nports-1)
#
#        # inject packet past the warmup period
#
#        if ( NUM_WARMUP_CYCLES < sim.ncycles < NUM_SAMPLE_CYCLES ):
#          src[i].append( mk_msg( i, dest, 0, sim.ncycles, num_ports=nports ) )
#          packets_generated += 1
#
#        # packet injection during warmup or drain phases
#
#        else:
#          src[i].append( mk_msg( i, dest, 0, INVALID_TIMESTAMP, num_ports=nports ) )
#          if ( sim.ncycles < NUM_SAMPLE_CYCLES ):
#            packets_generated += 1
#
#      # Inject from source queue
#
#      if ( len( src[i] ) > 0 ):
#        model.in_[i].msg.value = src[i][0]
#        model.in_[i].val.value = 1
#      else:
#        model.in_[i].val.value = 0
#
#      # Receive a packet
#
#      if ( model.out[i].val == 1 ):
#        timestamp = model.out[i].msg[0:32].uint()
#        all_packets_received += 1
#
#        # collect data for measurement packets
#
#        if ( timestamp != INVALID_TIMESTAMP ):
#          total_latency    += ( sim.ncycles - timestamp )
#          packets_received += 1
#          average_latency = total_latency / float( packets_received )
#
#      # Check if finished - drain phase
#
#      if ( sim.ncycles >= NUM_SAMPLE_CYCLES and
#           all_packets_received == packets_generated ):
#        average_latency = total_latency / float( packets_received )
#        sim_done = True
#        break
#
#      # Pop the source queue
#
#      if ( model.in_[i].rdy == 1 ) and ( len( src[i] ) > 0 ):
#        src[i].popleft()
#
#    # print line trace if enables
#
#    if trace:
#      sim.print_line_trace()
#
#    # advance simulation
#
#    sim.cycle()
#
#    # if in verbose mode, print stats every 100 cycles
#
#    if sim.ncycles % 100 == 1 and verbose:
#      print( "{:4}: gen {:5} recv {:5}"
#             .format(sim.ncycles, packets_generated, all_packets_received) )
#
#  # return the calculated average_latency and count of packets received
#
#  return [average_latency, packets_received, sim.ncycles]

#-------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------

def main():
  print 'Hello world'

  opts = parse_cmdline()

  # Determine which model to use in the simulator

  topology_dict = {
    'Ring'  : RingNetworkRTL, 
    'Mesh'  : MeshNetworkRTL, 
    'Torus' : TorusNetworkRTL,
    'Bf'    : BfNetworkRTL
  }

  dump_vcd = None
#  if opts.dump_vcd:
#    dump_vcd = "net-{}-{}.vcd".format( opts.impl, opts.pattern )

  results = simulate( topology_dict[ opts.topology ], opts.routers, 
            opts.routers/opts.rows, opts.rows, opts.injection_rate, 
            opts.pattern, 500, dump_vcd, opts.trace, opts.verbose )

  if opts.stats:
    print()
    print( "Pattern:        " + opts.pattern )
    print( "Injection rate: %d" % opts.injection_rate )
    print()
#    print( "Average Latency = %.1f" % results[0] )
#    print( "Num Packets     = %d" % results[1] )
#    print( "Total cycles    = %d" % results[2] )
#    print()



  # sweep mode: sweep the injection rate until the network is saturated.
  # we assume the latency is 100 when the network is saturated.

#  if opts.sweep:
#
#    print()
#    print( "Pattern: " + opts.pattern )
#    print()
#    print( "{:<20} | {:<20}".format( "Injection rate (%)", "Avg. Latency" ) )
#
#    inj             = 0
#    avg_lat         = 0
#    zero_load_lat   = 0
#    running_avg_lat = 0.0
#    inj_shamt_mult  = 5
#    inj_shamt       = 0.0
#    inj_step        = 5 if opts.impl == "bus" else 10 # ring
#
#    while avg_lat <= 100:
#
#      results = simulate( impl_dict[ opts.impl ], opts.num_nodes, opts.net_width, opts.net_height, 
#                          max(inj,1), opts.pattern, 500, opts.dump_vcd, opts.trace, opts.verbose )
#
#      avg_lat = results[0]
#
#      print( "{:<20} | {:<20.1f}".format( max(inj,1), avg_lat ) )
#
#      if inj == 0:
#        zero_load_lat = avg_lat
#
#      # dynamically reduce inj_step depending on the slope
#      if running_avg_lat == 0.0:
#        running_avg_lat = int(avg_lat)
#      else:
#        running_avg_lat = 0.5 * int(avg_lat) + 0.5 * int(running_avg_lat)
#
#      inj_shamt = ( (int(avg_lat) / running_avg_lat) - 1 ) * inj_shamt_mult
#      inj_step  = inj_step >> int(inj_shamt)
#      if inj_step < 1:
#        inj_step = 1
#      inj += inj_step
#
#    print()
#    print( "Zero-load latency = %.1f" % zero_load_lat )
#    print()
#
#  # Single run mode:
#
#  else:
#
#    dump_vcd = None
#    if opts.dump_vcd:
#      dump_vcd = "net-{}-{}.vcd".format( opts.impl, opts.pattern )
#
#    results = simulate( impl_dict[ opts.impl ], opts.num_nodes, opts.net_width, opts.net_height, 
#                        opts.injection_rate, opts.pattern, 500, dump_vcd, opts.trace, opts.verbose )
#
#    if opts.stats:
#      print()
#      print( "Pattern:        " + opts.pattern )
#      print( "Injection rate: %d" % opts.injection_rate )
#      print()
#      print( "Average Latency = %.1f" % results[0] )
#      print( "Num Packets     = %d" % results[1] )
#      print( "Total cycles    = %d" % results[2] )
#      print()

main()
