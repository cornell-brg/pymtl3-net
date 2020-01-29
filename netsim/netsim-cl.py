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
#  --mode              Choose model
#                      FL  : functional-level models
#                      CL  : cycle-level models
#                      RTL : register-transfer-level models
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

import argparse
import os
import re
import sys
import time
from collections import deque
from random import randint, seed

from bflynet.BflyNetworkRTL import BflyNetworkRTL
from cmeshnet.CMeshNetworkRTL import CMeshNetworkRTL
from meshnet.MeshNetworkCL import MeshNetworkCL, WrappedMeshNetCL
from meshnet.MeshNetworkRTL import MeshNetworkRTL
from ocnlib.ifcs.packets import *
from ocnlib.ifcs.positions import *
from pymtl3 import *
from pymtl3.stdlib.test import TestVectorSimulator
#from crossbar.CrossbarRTL     import CrossbarRTL
from ringnet.RingNetworkRTL import RingNetworkRTL
from torusnet.TorusNetworkRTL import TorusNetworkRTL

sim_dir = os.path.dirname( os.path.abspath( __file__ ) )
while sim_dir:
  if os.path.exists( sim_dir + os.path.sep + ".pymtl-python-path" ):
    sys.path.insert(0,sim_dir)
    # include the pymtl environment here
    # sys.path.insert(0,sim_dir + "/../pymtl3/")
    break
  sim_dir = os.path.dirname(sim_dir)


#from meshnet.MeshNetworkFL    import MeshNetworkFL




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
                       default = 8,
                       action  = "store",
                       help    = "number of inports in each router."       )

  parser.add_argument( "--router-outports",
                       type    = int,
                       default = 8,
                       action  = "store",
                       help    = "number of outports in each router."      )

  parser.add_argument( "--terminals-each",
                       type    = int,
                       default = 4,
                       action  = "store",
                       help    = "number of terminals attached to router." )

  opts = parser.parse_args()
  if opts.help: parser.error()
  return opts

#--------------------------------------------------------------------------
# Global Constants
#--------------------------------------------------------------------------

NUM_WARMUP_CYCLES   = 100
NUM_SAMPLE_CYCLES   = 500 + NUM_WARMUP_CYCLES
INVALID_TIMESTAMP   = 0

#--------------------------------------------------------------------------
# simulate
#--------------------------------------------------------------------------

def simulate( opts, injection_rate, pattern, drain_limit, dump_vcd, trace, verbose ):

  # Determine which model to use in the simulator

  topology_dict = {
    'Mesh'     : WrappedMeshNetCL,
  }

  # Simulation Variables

  num_nodes             = opts.routers

  average_latency       = 0
  packets_generated     = 0
  packets_received      = 0
  all_packets_received  = 0
  total_latency         = 0
  drain_cycles          = 0
  sim_done              = False

  # Instantiate and elaborate a ring network

  if opts.topology == "Ring":
    NetModel = topology_dict[ "Ring" ]
    RingPos = mk_ring_pos( opts.routers )
    PacketType = mk_ring_pkt_timestamp( opts.routers, vc = 2,
            max_time = NUM_SAMPLE_CYCLES )
    model = NetModel( PacketType, RingPos, opts.routers, 0 )
    model.set_param( "top.routers*.route_units*.construct", num_routers=opts.routers)

  elif opts.topology == "Mesh":
    NetModel = topology_dict[ "Mesh" ]
    net_width = opts.routers/opts.rows
    net_height = opts.rows
    MeshPos = mk_mesh_pos( net_width, net_height )
    PacketType = mk_mesh_pkt_timestamp( net_width, net_height,
                 payload_nbits = 1, max_time = NUM_SAMPLE_CYCLES )
    model = NetModel( PacketType, MeshPos, net_width, net_height, 0 )

  elif opts.topology == "Torus":
    NetModel = topology_dict[ "Torus" ]
    net_width = opts.routers/opts.rows
    net_height = opts.rows
    MeshPos = mk_mesh_pos( net_width, net_height )
    PacketType = mk_mesh_pkt_timestamp( net_width, net_height, vc = 2,
            max_time = NUM_SAMPLE_CYCLES )
    model = NetModel( PacketType, MeshPos, net_width, net_height, 0 )

  elif opts.topology == "CMesh":
    NetModel = topology_dict[ "CMesh" ]
    net_width = opts.routers/opts.rows
    net_height = opts.rows
    inports   = opts.router_inports
    outports  = opts.router_outports
    term_each = opts.terminals_each
    MeshPos = mk_mesh_pos( net_width, net_height )
    PacketType = mk_cmesh_pkt_timestamp( net_width, net_height,
                 inports, outports,
                 payload_nbits = 1, max_time = NUM_SAMPLE_CYCLES )
    model = NetModel( PacketType, MeshPos, net_width, net_height,
                      term_each, 0 )

  elif opts.topology == "Butterfly":
    NetModel = topology_dict[ "Butterfly" ]
    k_ary = 4
    n_fly = 3
    num_nodes = k_ary * ( k_ary ** ( n_fly - 1 ) )
    num_routers   = n_fly * ( k_ary ** ( n_fly - 1 ) )
    MeshPos = mk_bfly_pos( k_ary, n_fly )
    PacketType = mk_bfly_pkt_timestamp( k_ary, n_fly,
                 payload_nbits = 1, max_time = NUM_SAMPLE_CYCLES )
    model = NetModel( PacketType, MeshPos, k_ary, n_fly, 0 )
    model.set_param( "top.routers*.construct", k_ary=k_ary )
    model.set_param( "top.routers*.route_units*.construct", n_fly=n_fly )


  model.apply( SimulationPass() )

  # Source Queues - Modeled as Bypass Queues
  src = [ deque() for x in range( num_nodes ) ]

  # Run the simulation

  model.sim_reset()
  # for i in range( num_nodes ):
  #   model.send[i].rdy = 1

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
          dest = ( randint( 0, num_nodes-1 ) ) & (num_nodes/2-1) |\
                 ( i & (num_nodes/2) )
        elif pattern == "opposite":
          dest = ( i + 2 ) % num_nodes
        elif pattern == "neighbor":
          dest = ( i + 1 ) % num_nodes
        elif pattern == "complement":
          dest = i ^ (num_nodes-1)

        # inject packet past the warmup period

        if ( NUM_WARMUP_CYCLES < ncycles < NUM_SAMPLE_CYCLES ):
          if opts.topology == "Ring":
            if dest < i and i - dest <= num_nodes/2:
              opaque = 0
            elif dest > i and dest - i <= num_nodes/2:
              opaque = 0
            else:
              opaque = 0

            pkt = PacketType( i, dest, 0, opaque, 98+i+ncycles, ncycles )

          elif opts.topology == "Mesh":
#            net_width = opts.routers / opts.rows
            pkt = PacketType( i%net_width, i/net_width, dest%net_width,
                    dest/net_width, 0, 6, ncycles )

          elif opts.topology == "Torus":
#            net_width = opts.routers / opts.rows
            pkt = PacketType( i%net_width, i/net_width, dest%net_width,
                    dest/net_width, 0, 0, 6, ncycles )

          elif opts.topology == "CMesh":
            pkt = PacketType( (i/term_each)%net_width,
                              (i/term_each)/net_width,
                              (dest/term_each)%net_width,
                              (dest/term_each)/net_width,
                              dest%term_each,
                              0, 6, ncycles )

          elif opts.topology == "Butterfly":
            r_rows = k_ary ** ( n_fly - 1 )
#            DstType = mk_bits( clog2( r_rows ) * n_fly )
            if r_rows == 1 or k_ary == 1:
              DstType = mk_bits( n_fly )
            else:
              DstType = mk_bits( clog2( k_ary ) * n_fly )
            bf_dst = DstType(0)
            tmp = 0
            dst = dest
            for index in range( n_fly ):
              tmp = dst / (k_ary**(n_fly-index-1))
              dst = dst % (k_ary**(n_fly-index-1))
              bf_dst = DstType(bf_dst | DstType(tmp))
              if index != n_fly - 1:
                if k_ary == 1:
                  bf_dst = bf_dst * 2
                else:
                  bf_dst = bf_dst * k_ary
            pkt = PacketType( i, bf_dst, 0, 6, ncycles )

          src[i].append( pkt )
          packets_generated += 1

        # packet injection during warmup or drain phases

        else:
          if opts.topology == "Ring":
            if dest < i and i - dest <= num_nodes/2:
              opaque = 0
            elif dest > i and dest - i <= num_nodes/2:
              opaque = 0
            else:
              opaque = 0
            pkt = PacketType( i, dest, opaque, 0, 98+i+ncycles, INVALID_TIMESTAMP )

          elif opts.topology == "Mesh":
            pkt = PacketType( i%net_width, i/net_width, dest%net_width,
                    dest/net_width, 0, 6, INVALID_TIMESTAMP )
#            pkt = mk_mesh_pkt_timestamp( i%net_width, i/net_width, dest%net_width,
#                    dest/net_width, 1, 6, INVALID_TIMESTAMP )

          elif opts.topology == "Torus":
            pkt = PacketType( i%net_width, i/net_width, dest%net_width,
                    dest/net_width, 0, 0, 6, INVALID_TIMESTAMP )

          elif opts.topology == "CMesh":
            pkt = PacketType( (i/term_each)%net_width,
                              (i/term_each)/net_width,
                              (dest/term_each)%net_width,
                              (dest/term_each)/net_width,
                              dest%term_each,
                              0, 6, INVALID_TIMESTAMP )

          elif opts.topology == "Butterfly":
            r_rows = k_ary ** ( n_fly - 1 )
#            DstType = mk_bits( clog2( r_rows ) * n_fly )
            if r_rows == 1 or k_ary == 1:
              DstType = mk_bits( n_fly )
            else:
              DstType = mk_bits( clog2( k_ary ) * n_fly )
            bf_dst = DstType(0)
            tmp = 0
            dst = dest
            for index in range( n_fly ):
              tmp = dst / (k_ary**(n_fly-index-1))
              dst = dst % (k_ary**(n_fly-index-1))
              bf_dst = DstType(bf_dst | DstType(tmp))
              if index != n_fly - 1:
                if k_ary == 1:
                  bf_dst = bf_dst * 2
                else:
                  bf_dst = bf_dst * k_ary
            pkt = PacketType( i, bf_dst, 0, 6, INVALID_TIMESTAMP )

          src[i].append( pkt )
          if ( ncycles < NUM_SAMPLE_CYCLES ):
            packets_generated += 1

      # Inject from source queue

      if ( len( src[i] ) > 0 ):
        if model.recv[i].rdy():
          model.recv[i]( src[i][0] )

      # Receive a packet
      # FIXME: append queues at send side.
      if model.give[i].rdy():
        pkt = model.give[i]()
        timestamp =pkt.timestamp
        all_packets_received += 1

        # collect data for measurement packets
        if ( timestamp != INVALID_TIMESTAMP ):
          total_latency    += ( ncycles - timestamp )
          packets_received += 1
          average_latency = total_latency / float( packets_received )

      # Check if finished - drain phase
      #print 'all_packets_received: ', all_packets_received
      #print 'packets_generated: ', packets_generated

      if ( ncycles >= NUM_SAMPLE_CYCLES and
           all_packets_received >= packets_generated ):
        average_latency = total_latency / float( packets_received )
        sim_done = True
        break

      # Pop the source queue

      if model.recv[i].rdy() and ( len( src[i] ) > 0 ):
        src[i].popleft()

    # print line trace if enables

    # advance simulation

    if trace:
      print "{:3}:{}".format( ncycles, model.line_trace() )

    model.tick()
    ncycles += 1

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

  dump_vcd = None
  start_time      = 0
  end_time        = 1

  # sweep mode: sweep the injection rate until the network is saturated.
  # we assume the latency is 100 when the network is saturated.

  if opts.sweep:

    print()
    print( "Pattern: " + opts.pattern )
    print()
    print( "{:<20} | {:<20} | {:<20} | {:<20}".\
            format( "Injection rate (%)", "Avg. Latency", \
                    "Sim.Time (sec)", "Sim.Speed (cyc/s)") )

    inj             = 0
    avg_lat         = 0
    zero_load_lat   = 0
    running_avg_lat = 0.0
    inj_shamt_mult  = 5
    inj_shamt       = 0.0
    inj_step        = 5 if opts.topology == "bus" else 10 # ring

    while avg_lat <= 500 and inj <= 100:

      start_time = time.time()

      results = simulate( opts, max(inj,1), opts.pattern, 500,
              opts.dump_vcd, opts.trace, opts.verbose )

      end_time = time.time()

      avg_lat = results[0]

      print( "{:<20} | {:<20.1f} | {:<20.1f} | {:<20.1f}".\
              format( max(inj,1), avg_lat, (end_time - start_time),
              results[2]/(end_time - start_time)) )

      if inj == 0:
        zero_load_lat = avg_lat

      # dynamically reduce inj_step depending on the slope
      if running_avg_lat == 0.0:
        running_avg_lat = int(avg_lat)
      else:
        running_avg_lat = 0.5 * int(avg_lat) + 0.5 * int(running_avg_lat)

#      inj_shamt = ( (int(avg_lat) / running_avg_lat) - 1 ) * inj_shamt_mult
#      inj_step  = inj_step >> int(inj_shamt)
#      if inj_step < 1:
#        inj_step = 1
#      inj += inj_step
      inj += 10

    print()
    print( "Zero-load latency = %.1f" % zero_load_lat )
    print()

  else:
    start_time = time.time()

    results = simulate( opts, opts.injection_rate, opts.pattern, 500,
            dump_vcd, opts.trace, opts.verbose )

    end_time = time.time()

  if opts.stats and not opts.sweep:
    print()
    print( "Pattern:         " + opts.pattern )
    print( "Injection rate:  %d" % opts.injection_rate )
    print()
    print( "Average Latency  = %.1f" % results[0] )
    print( "Num Packets      = %d" % results[1] )
    print( "Total cycles     = %d" % results[2] )
    print( "Simulation time  = %.1f sec" % (end_time - start_time) )
    print( "Simulation speed = %.1f cycle/sec" % \
            (results[2]/(end_time - start_time)) )
    print()

main()
