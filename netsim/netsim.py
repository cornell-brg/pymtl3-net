#!/usr/bin/env python
#=========================================================================
# netsim.py [options]
#=========================================================================
#
#  -h --help           Display this message
#  -v --verbose        Verbose mode
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
#  --topology          Choose NoC topology
#                      Ring     : ring network
#                      Mesh     : mesh network
#                      CMesh    : concentrated mesh network
#                      Torus    : torus network
#                      Butterfly: K-ary n-fly butterfly network
#
#  --virtual-channels  Number of virtual channels
#
#  --routing-strategy  Choose a routing algorithm
#                      DORX : Dimension Order Routing - X
#                      DORY : Dimension Order Routing - Y 
#
#  --routers           Number of routers in network
#
#  --terminals-each    Number of terminals attached to router (for CMesh)
#
#  --rows              Number of rows of routers in network
#
#  --router-inports    Number of inports in each router
#
#  --router-outports   Number of outports in each router
#
#  --channel-latency   Latency of the channel between routers
#
# The OCN generator simulator. Choose an implementation and an
# access pattern to execute. Use --stats to display statistics about the
# simulation.
#
# Author : Cheng Tan
# Date   : April 14, 2018

#from __future__ import print_function

# Hack to add project root to python path

import os
import sys
import argparse
import re

from collections             import deque
from random                  import seed, randint

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

from pymtl                    import *
from meshnet.MeshNetworkRTL   import MeshNetworkRTL
from cmeshnet.CMeshNetworkRTL import CMeshNetworkRTL
from ringnet.RingNetworkRTL   import RingNetworkRTL
from torusnet.TorusNetworkRTL import TorusNetworkRTL
from bflynet.BflyNetworkRTL   import BflyNetworkRTL
from ocn_pclib.ifcs.Packet    import *
from ocn_pclib.ifcs.Position  import *
from pclib.test               import TestVectorSimulator

seed(0xdeadbeef)

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
                       choices = [ 'Ring', 'Mesh', 'CMesh', 
                                   'Torus', 'Butterfly' ],
                       help    = "topology can be applied in the network." )

  parser.add_argument( "--router-latency",   
                       type    = int, 
                       default = 1,
                       action  = "store",
                       help    = "number of pipeline stages in router."    )

  parser.add_argument( "--channel-latency",     
                       type    = int, 
                       default = 1,
                       action  = "store",
                       help    = "number of input stages in router."       )

  parser.add_argument( "--link-width-bits",  
                       type    = int, 
                       default = 128,
                       action  = "store",
                       help    = "width in bits for all links."            )

  parser.add_argument( "--virtual-channels",  
                       type    = int, 
                       default = 4,
                       action  = "store",
                       help    = "number of virtual channels."             )

  parser.add_argument( "--routing-strategy", 
                       type    = str,
                       default = "DORY",
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

  parser.add_argument( "--terminals-each",  
                       type    = int, 
                       default = 1,
                       action  = "store",
                       help    = "number of terminals attached to router." )

  opts = parser.parse_args()
  if opts.help: parser.error()
  return opts

#--------------------------------------------------------------------------
# Global Constants
#--------------------------------------------------------------------------

NUM_WARMUP_CYCLES   = 200
NUM_SAMPLE_CYCLES   = 200 + NUM_WARMUP_CYCLES
INVALID_TIMESTAMP   = 0

#--------------------------------------------------------------------------
# simulate
#--------------------------------------------------------------------------

def simulate( NetModel, num_nodes, net_width, net_height,
              injection_rate, pattern, drain_limit, dump_vcd, trace, verbose ):

  num_nodes = num_nodes

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

  sim = model.apply( SimpleSim )

#  model.elaborate()
#
  # Source Queues - Modeled as Bypass Queues
  src = [ deque() for x in range( num_nodes ) ]
  # Run the simulation

  model.sim_reset()
  for i in range( num_nodes ):
    model.send[i].rdy = 1

  ncycles = 0
  while not sim_done:
    # Iterate over all terminals
    for i in range( num_nodes ):

      # Generate packet

      if ( randint( 1, 100 ) <= injection_rate ):

        # traffic pattern based dest selection
        if   pattern == "urandom":
          dest = randint( 0, num_nodes-1 )
        elif pattern == "partition2":
          dest = ( randint( 0, num_nodes-1 ) ) & (num_nodes/2-1) | ( i & (num_nodes/2) )
        elif pattern == "opposite":
          dest = ( i + 2 ) % num_nodes
        elif pattern == "neighbor":
          dest = ( i + 1 ) % num_nodes
        elif pattern == "complement":
          dest = i ^ (num_nodes-1)

        # inject packet past the warmup period

        if ( NUM_WARMUP_CYCLES < ncycles < NUM_SAMPLE_CYCLES ):
          pkt = mk_pkt_timestamp( i%net_width, i/net_width, dest%net_width,
                  dest/net_width, 1, 6, ncycles )
          src[i].append( pkt )
          packets_generated += 1

        # packet injection during warmup or drain phases

        else:
          pkt = mk_pkt_timestamp( i%net_width, i/net_width, dest%net_width,
                  dest/net_width, 1, 6, INVALID_TIMESTAMP )
          src[i].append( pkt )
          if ( ncycles < NUM_SAMPLE_CYCLES ):
            packets_generated += 1

      # Inject from source queue

      if ( len( src[i] ) > 0 ):
        model.recv[i].msg = src[i][0]
        model.recv[i].en  = 1
      else:
        model.recv[i].en  = 0

      # Receive a packet

      if ( model.send[i].en == 1 ):
        timestamp = model.send[i].msg.timestamp
        all_packets_received += 1

        # collect data for measurement packets

        if ( timestamp != INVALID_TIMESTAMP ):
          total_latency    += ( ncycles - timestamp )
          packets_received += 1
          average_latency = total_latency / float( packets_received )

      # Check if finished - drain phase

      if ( ncycles >= NUM_SAMPLE_CYCLES and
           all_packets_received == packets_generated ):
        average_latency = total_latency / float( packets_received )
        sim_done = True
        break

      # Pop the source queue

      if ( model.recv[i].rdy == 1 ) and ( len( src[i] ) > 0 ):
        src[i].popleft()

    # print line trace if enables

    # advance simulation

    model.tick()
    ncycles += 1
    if trace:
#      sim.print_line_trace()
      print "{}:{}".format( ncycles, model.line_trace() )
    # if in verbose mode, print stats every 100 cycles

    if ncycles % 100 == 1 and verbose:
      print( "{:4}: gen {:5} recv {:5}"
             .format(ncycles, packets_generated, all_packets_received) )

  # return the calculated average_latency and count of packets received

  return [average_latency, packets_received, ncycles]

#-------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------

def main():

  opts = parse_cmdline()

  # Determine which model to use in the simulator

  topology_dict = {
    'Ring'     : RingNetworkRTL, 
    'Mesh'     : MeshNetworkRTL, 
    'CMesh'    : CMeshNetworkRTL, 
    'Torus'    : TorusNetworkRTL,
    'Butterfly': BflyNetworkRTL
  }

  dump_vcd = None
#  if opts.dump_vcd:
#    dump_vcd = "net-{}-{}.vcd".format( opts.impl, opts.pattern )

  print '==================== Config ====================='
  print ' Topology: {}; Routers: {}; Rows: {}'.format(opts.topology, 
        opts.routers, opts.rows)

  # sweep mode: sweep the injection rate until the network is saturated.
  # we assume the latency is 100 when the network is saturated.

  if opts.sweep:

    print()
    print( "Pattern: " + opts.pattern )
    print()
    print( "{:<20} | {:<20}".format( "Injection rate (%)", "Avg. Latency" ) )

    inj             = 0
    avg_lat         = 0
    zero_load_lat   = 0
    running_avg_lat = 0.0
    inj_shamt_mult  = 5
    inj_shamt       = 0.0
    inj_step        = 5 if opts.topology == "bus" else 10 # ring

    while avg_lat <= 100:

      results = simulate( topology_dict[ opts.topology ], opts.routers, 
                opts.routers/opts.rows, opts.rows, max(inj,1), 
                opts.pattern, 500, opts.dump_vcd, opts.trace, opts.verbose )

      avg_lat = results[0]

      print( "{:<20} | {:<20.1f}".format( max(inj,1), avg_lat ) )

      if inj == 0:
        zero_load_lat = avg_lat

      # dynamically reduce inj_step depending on the slope
      if running_avg_lat == 0.0:
        running_avg_lat = int(avg_lat)
      else:
        running_avg_lat = 0.5 * int(avg_lat) + 0.5 * int(running_avg_lat)

      inj_shamt = ( (int(avg_lat) / running_avg_lat) - 1 ) * inj_shamt_mult
      inj_step  = inj_step >> int(inj_shamt)
      if inj_step < 1:
        inj_step = 1
      inj += inj_step

    print()
    print( "Zero-load latency = %.1f" % zero_load_lat )
    print()

  else:
    results = simulate( topology_dict[ opts.topology ], opts.routers, 
          opts.routers/opts.rows, opts.rows, opts.injection_rate, 
          opts.pattern, 500, dump_vcd, opts.trace, opts.verbose )

  if opts.stats:
    print()
    print( "Pattern:        " + opts.pattern )
    print( "Injection rate: %d" % opts.injection_rate )
    print()
    print( "Average Latency = %.1f" % results[0] )
    print( "Num Packets     = %d" % results[1] )
    print( "Total cycles    = %d" % results[2] )
    print()

main()

