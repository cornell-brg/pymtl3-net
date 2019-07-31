#!/usr/bin/env python
"""
=========================================================================
pyocn.py
=========================================================================
Example of PyOCN for modeling, testing, and evaluating.

Author : Cheng Tan
  Date : July 30, 2019
"""
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

import os
import sys
import argparse
import re

from collections import deque
from random      import seed, randint

sim_dir = os.path.dirname( os.path.abspath( __file__ ) )
os.system(sim_dir)
while sim_dir:
  if os.path.exists( sim_dir + os.path.sep + ".pymtl-python-path" ):
    sys.path.insert(0,sim_dir)
    # include the pymtl environment here
    # sys.path.insert(0,sim_dir + "/../pymtl3/")
    break
  sim_dir = os.path.dirname(sim_dir)
  os.system(sim_dir)

#from meshnet.MeshNetworkFL    import MeshNetworkFL
#from crossbar.CrossbarRTL     import CrossbarRTL
from pymtl3                   import *
from meshnet.MeshNetworkCL    import MeshNetworkCL
from ringnet.RingNetworkRTL   import RingNetworkRTL
from meshnet.MeshNetworkRTL   import MeshNetworkRTL
from cmeshnet.CMeshNetworkRTL import CMeshNetworkRTL
from torusnet.TorusNetworkRTL import TorusNetworkRTL
from bflynet.BflyNetworkRTL   import BflyNetworkRTL
from ocn_pclib.ifcs.packets   import *
from ocn_pclib.ifcs.positions import *
from pymtl3.stdlib.test       import TestVectorSimulator

import time

seed(0xdeadbeef)

#-------------------------------------------------------------------------
# Command line processing
#-------------------------------------------------------------------------

#--------------------------------------------------------------------------
# generate
#--------------------------------------------------------------------------

def generate():
  pass

#--------------------------------------------------------------------------
# characterize
#--------------------------------------------------------------------------

def characterize():
  pass

#--------------------------------------------------------------------------
# simulate
#--------------------------------------------------------------------------

# Global constants for simulation

NUM_WARMUP_CYCLES   = 100
NUM_SAMPLE_CYCLES   = 500 + NUM_WARMUP_CYCLES
INVALID_TIMESTAMP   = 0

#def simulate( opts, injection_rate, pattern, drain_limit, dump_vcd, trace, verbose ):
def simulate( model, topology, nodes, rows, channel_lat, injection, pattern ):

  routers         = nodes
  channel_latency = channel_lat
  injection_rate  = injection
  net             = None

  # Simulation Variables

  average_latency       = 0
  packets_generated     = 0
  packets_received      = 0
  all_packets_received  = 0
  total_latency         = 0
  drain_cycles          = 0
  sim_done              = False

  # Determine which model to use in the simulator

  if model == "CL":
    if topology == "ring":
      NetModel = RingNetworkCL
    elif topology == "mesh":
      NetModel = MeshNetworkCL
    elif topology == "cmesh":
      NetModel = CMeshNetworkCL
    elif topology == "torus":
      NetModel = TorusNetworkCL
    elif topology == "bfly":
      NetModel = BflyNetworkCL

  elif model == "RTL":
    # Instantiate and elaborate a ring network

    if topology  == "Ring":
      NetModel   = RingNetworkRTL
      RingPos    = mk_ring_pos( routers )
      PacketType = mk_ring_pkt_timestamp( routers, nvcs = 2,
                   max_time = NUM_SAMPLE_CYCLES )
      net      = NetModel( PacketType, RingPos, routers, 0 )
#      net.set_param( "top.routers*.route_units*.construct", num_routers=routers)
  
    elif topology == "Mesh":
      NetModel    = MeshNetworkRTL
      net_width   = int(routers/rows)
      net_height  = rows
      MeshPos     = mk_mesh_pos( net_width, net_height )
      PacketType  = mk_mesh_pkt_timestamp( net_width, net_height,
                    payload_nbits = 1, max_time = NUM_SAMPLE_CYCLES )
      net         = NetModel( PacketType, MeshPos, net_width, net_height, 0 )
  
    elif topology == "Torus":
      NetModel    = TorusNetworkRTL
      net_width   = routers/rows
      net_height  = rows
      MeshPos     = mk_mesh_pos( net_width, net_height )
      PacketType  = mk_mesh_pkt_timestamp( net_width, net_height, nvcs = 2,
                    max_time = NUM_SAMPLE_CYCLES )
      net         = NetModel( PacketType, MeshPos, net_width, net_height, 0 )
      # model.set_param('top.routers*.route_units*.construct', ncols=net_width )
      # model.set_param('top.routers*.route_units*.construct', nrows=net_height)
  
    elif topology == "CMesh":
      NetModel    = CMeshNetworkRTL
      routers     = rows * rows
      net_width   = routers/rows
      net_height  = rows
      term_each   = nodes/routers
      inports     = term_each + 4
      outports    = term_each + 4
      MeshPos     = mk_mesh_pos( net_width, net_height )
      PacketType  = mk_cmesh_pkt_timestamp( net_width, net_height,
                    inports, outports, payload_nbits = 1, 
                    max_time = NUM_SAMPLE_CYCLES )
      net         = NetModel( PacketType, MeshPos, net_width, net_height,
                    term_each, 0 )
  
    elif topology == "Butterfly":
      NetModel    = BflyNetworkRTL
      k_ary       = 4
      n_fly       = 3
      num_nodes   = k_ary * ( k_ary ** ( n_fly - 1 ) )
      num_routers = n_fly * ( k_ary ** ( n_fly - 1 ) )
      MeshPos     = mk_bfly_pos( k_ary, n_fly )
      PacketType  = mk_bfly_pkt_timestamp( k_ary, n_fly,
                    payload_nbits = 1, max_time = NUM_SAMPLE_CYCLES )
      net         = NetModel( PacketType, MeshPos, k_ary, n_fly, 0 )
      net.set_param( "top.routers*.construct", k_ary=k_ary )
      net.set_param( "top.routers*.route_units*.construct", n_fly=n_fly )

#  net.elaborate()
  sim = net.apply( DynamicSim )

  # Source Queues - Modeled as Bypass Queues
  src = [ deque() for x in range( nodes ) ]

  # Run the simulation

  net.sim_reset()
  for i in range( nodes ):
    net.send[i].rdy = 1

    if topology == "Mesh":
      XYType = mk_bits( clog2( net_width ) )
      net.pos_x[i] = XYType(i%net_width)
      net.pos_y[i] = XYType(i/net_height)

  ncycles = 0

  while not sim_done:
    # Iterate over all terminals
    for i in range( nodes ):

      # Generate packet

      if ( randint( 1, 100 ) <= injection_rate ):

        # traffic pattern based dest selection
        if   pattern == "urandom":
          dest = randint( 0, nodes-1 )
        elif pattern == "partition":
          dest = ( randint( 0, nodes-1 ) ) & (nodes/2-1) |\
                 ( i & (nodes/2) )
        elif pattern == "opposite":
          dest = ( i + 2 ) % nodes
        elif pattern == "neighbor":
          dest = ( i + 1 ) % nodes
        elif pattern == "complement":
          dest = i ^ (nodes-1)

        # inject packet past the warmup period

        if ( NUM_WARMUP_CYCLES < ncycles < NUM_SAMPLE_CYCLES ):
          if topology == "Ring":
            if dest < i and i - dest <= nodes/2:
              opaque = 0
            elif dest > i and dest - i <= nodes/2:
              opaque = 0
            else:
              opaque = 0

            pkt = PacketType( i, dest, 0, opaque, 98+i+ncycles, ncycles )

          elif topology == "Mesh":
#            net_width = opts.routers / opts.rows
            pkt = PacketType( i%net_width, i/net_width, dest%net_width,
                    dest/net_width, 0, 6, ncycles )

          elif topology == "Torus":
#            net_width = opts.routers / opts.rows
            pkt = PacketType( i%net_width, i/net_width, dest%net_width,
                    dest/net_width, 0, 0, 6, ncycles )

          elif topology == "CMesh":
            pkt = PacketType( (i/term_each)%net_width,
                              (i/term_each)/net_width,
                              (dest/term_each)%net_width,
                              (dest/term_each)/net_width,
                              dest%term_each,
                              0, 6, ncycles )

          elif topology == "Butterfly":
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
          if topology == "Ring":
            if dest < i and i - dest <= num_nodes/2:
              opaque = 0
            elif dest > i and dest - i <= num_nodes/2:
              opaque = 0
            else:
              opaque = 0
            pkt = PacketType( i, dest, opaque, 0, 98+i+ncycles, INVALID_TIMESTAMP )

          elif topology == "Mesh":
            pkt = PacketType( i%net_width, i/net_width, dest%net_width,
                    dest/net_width, 0, 6, INVALID_TIMESTAMP )
#            pkt = mk_mesh_pkt_timestamp( i%net_width, i/net_width, dest%net_width,
#                    dest/net_width, 1, 6, INVALID_TIMESTAMP )

          elif topology == "Torus":
            pkt = PacketType( i%net_width, i/net_width, dest%net_width,
                    dest/net_width, 0, 0, 6, INVALID_TIMESTAMP )

          elif topology == "CMesh":
            pkt = PacketType( (i/term_each)%net_width,
                              (i/term_each)/net_width,
                              (dest/term_each)%net_width,
                              (dest/term_each)/net_width,
                              dest%term_each,
                              0, 6, INVALID_TIMESTAMP )

          elif topology == "Butterfly":
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
        if net.recv[i].rdy:
          net.recv[i].msg = src[i][0]
          net.recv[i].en  = 1
#          print 'injected pkt: ', src[i][0]
        else:
          net.recv[i].en  = 0
      else:
        net.recv[i].en  = 0

      # Receive a packet

      if ( net.send[i].en == 1 ):
        timestamp = net.send[i].msg.timestamp
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

      if ( net.recv[i].rdy == 1 ) and ( len( src[i] ) > 0 ):
        src[i].popleft()

    # print line trace if enables

    # advance simulation

    print( "{:3}:{}".format( ncycles, net.line_trace() ))

    net.tick()
    ncycles += 1

  # return the calculated average_latency and count of packets received

  return [average_latency, packets_received, ncycles]

#-------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------

from ruamel.yaml import YAML
from pathlib import Path

def main():

#  opts = parse_cmdline()

  path   = Path('config.yml')
  yaml   = YAML(typ='safe')
  config = yaml.load(path)

  print( config )
  print( config['topology'] )
  
  start_time      = 0
  end_time        = 1

  start_time = time.time()

  model     = config['model'][1]
  topology  = config['topology'][0]
  injection = config['injection'][0]
  pattern   = config['pattern'][0]
  results   = simulate( model, topology, config['nodes'], config['rows'],  
              config['channel_lat'], injection, pattern )
 
  end_time = time.time()

  print()
  print( "Pattern:         " + pattern )
  print( "Injection rate:  %d" % injection )
  print()
  print( "Average Latency  = %.1f" % results[0] )
  print( "Num Packets      = %d" % results[1] )
  print( "Total cycles     = %d" % results[2] )
  print( "Simulation time  = %.1f sec" % (end_time - start_time) )
  print( "Simulation speed = %.1f cycle/sec" % \
          (results[2]/(end_time - start_time)) )
  print()

main()

