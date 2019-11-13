#!/usr/bin/env python
"""
=========================================================================
main.py
=========================================================================
Example of PyOCN for modeling, testing, and evaluating.

Author : Cheng Tan
  Date : July 30, 2019
"""
import os
import sys
import argparse
import re

from collections import deque
from random      import seed, randint

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
from pymtl3.passes.yosys      import ImportPass, TranslationPass

import time

seed(0xdeadbeef)

#-------------------------------------------------------------------------
# Command line processing
#-------------------------------------------------------------------------

def generate( topology, terminals, dimension, channel_latency ):
  model = "RTL"
  perform( "generate", model, topology, terminals, dimension,
           channel_latency, 0, None, None )

#--------------------------------------------------------------------------
# verify using test cases.
#--------------------------------------------------------------------------

def verify( topology, terminals, dimension, channel_latency, packets ):
  model = "RTL"
  perform( "verify", model, topology, terminals, dimension,
           channel_latency, 0, None, packets )

#--------------------------------------------------------------------------
# simulate for single packet (from the first terminal to the last one).
#--------------------------------------------------------------------------

def simulate_1pkt( topology, terminals, dimension, channel_latency,
                   packets ):
  model = "RTL"
  perform( "simulate-1pkt", model, topology, terminals, dimension,
           channel_latency, 0, None, packets )

#--------------------------------------------------------------------------
# simulate to get latency vs. bandwidth.
#--------------------------------------------------------------------------

def simulate_lat_vs_bw( topology, terminals, dimension, channel_latency,
                        injection, pattern ):
  model = "RTL"
  return perform( "simulate-lat-vs-bw", model, topology, terminals,
                  dimension, channel_latency, injection, pattern, None )

#--------------------------------------------------------------------------
# perform function is generic for all the actions.
#--------------------------------------------------------------------------

# Global constants for simulation

NUM_WARMUP_CYCLES   = 10
NUM_SAMPLE_CYCLES   = 50 + NUM_WARMUP_CYCLES
INVALID_TIMESTAMP   = 0

def perform( action, model, topology, terminals, dimension,
             channel_latency, injection, pattern, packets ):

  routers         = terminals
#  injection_rate  = injection * 100
  injection_rate  = injection
  net             = None

  # Simulation Variables

  average_latency       = 0.0
  packets_generated     = 0
  packets_received      = 0
  all_packets_received  = 0
  total_latency         = 0
  drain_cycles          = 0
  sim_done              = False

  if model == "RTL":
    # Instantiate and elaborate a ring network

    if topology  == "Ring":
      NetModel   = RingNetworkRTL
      RingPos    = mk_ring_pos( routers )
      PacketType = mk_ring_pkt_timestamp( routers, payload_nbits = 32,
                   nvcs = 2, max_time = NUM_SAMPLE_CYCLES )
      net        = NetModel( PacketType, RingPos, routers, channel_latency )

    elif topology == "Mesh":
      NetModel    = MeshNetworkRTL
      net_width   = routers // dimension
      net_height  = dimension
      MeshPos     = mk_mesh_pos( net_width, net_height )
      PacketType  = mk_mesh_pkt_timestamp( net_width, net_height,
                    payload_nbits = 32, max_time = NUM_SAMPLE_CYCLES )
      net         = NetModel( PacketType, MeshPos,
                    net_width, net_height, channel_latency )

    elif topology == "Torus":
      NetModel    = TorusNetworkRTL
      net_width   = routers // dimension
      net_height  = dimension
      MeshPos     = mk_mesh_pos( net_width, net_height )
      PacketType  = mk_mesh_pkt_timestamp( net_width, net_height,
                    payload_nbits = 32, nvcs = 2,
                    max_time = NUM_SAMPLE_CYCLES )
      net         = NetModel( PacketType, MeshPos, net_width, net_height, 0 )

    elif topology == "CMesh":
      # TODO: need to provide parameters for different topology specifically.
      NetModel    = CMeshNetworkRTL
      routers     = dimension * dimension
      net_width   = routers // dimension
      net_height  = dimension
      term_each   = terminals // routers
      inports     = term_each + 4
      outports    = term_each + 4
      MeshPos     = mk_mesh_pos( net_width, net_height )
      PacketType  = mk_cmesh_pkt_timestamp( net_width, net_height,
                    inports, outports, payload_nbits = 32,
                    max_time = NUM_SAMPLE_CYCLES )
      net         = NetModel( PacketType, MeshPos, net_width, net_height,
                    term_each, 0 )

    elif topology == "Bfly":
      NetModel    = BflyNetworkRTL
      k_ary       = dimension
      temp_v      = terminals // k_ary
      n_fly       = 1
      while temp_v != 1:
        temp_v = temp_v // k_ary
        n_fly  = n_fly + 1
      # terminals   = k_ary * ( k_ary ** ( n_fly - 1 ) )
      num_routers = n_fly * ( k_ary ** ( n_fly - 1 ) )
      MeshPos     = mk_bfly_pos( k_ary, n_fly )
      PacketType  = mk_bfly_pkt_timestamp( k_ary, n_fly,
                    payload_nbits = 32, max_time = NUM_SAMPLE_CYCLES )
      net         = NetModel( PacketType, MeshPos, k_ary, n_fly, 0 )
      net.set_param( "top.routers*.construct", k_ary=k_ary )
      net.set_param( "top.routers*.route_units*.construct", n_fly=n_fly )

  net.elaborate()

  if action == "generate":
    os.system("[ ! -e "+topology+"NetworkRTL.sv ] || rm "+topology+"NetworkRTL.sv")
    net.yosys_translate = True
    net.apply( TranslationPass() )
    sim = net.apply( SimulationPass )
    os.system("mv "+topology+"*.sv "+topology+"NetworkRTL.sv")
    return

  if action == "simulate-1pkt":
    net.dump_vcd = True
    net.vcd_file_name = topology+"_sim1pkt"

  net.apply( SimulationPass )

  # Source Queues - Modeled as Bypass Queues
  src_queue = [ deque() for x in range( terminals ) ]

  # Run the simulation

  net.sim_reset()

  for i in range( terminals ):
    net.send[i].rdy = Bits1(1)

  ncycles = 0

  pkt_verify_queue = [[] for _ in range(terminals) ]

  verify_failed = False

  while not sim_done:
    # Iterate over all terminals
    for i in range( terminals ):

      # Generate packet

      if ( (action == "simulate-lat-vs-bw" and
            randint(1, 100) <= injection_rate) or
           ((action == "simulate-1pkt" or action == "verify") and
            len(packets) > 0 and int(packets[0]['src']) == i) ):

        if (action == "simulate-lat-vs-bw"):
          # traffic pattern based dest selection
          if   pattern == "urandom":
            dest = randint( 0, terminals-1 )
          elif pattern == "partition":
            dest = ( randint( 0, terminals-1 ) ) & (terminals // 2-1) |\
                   ( i & (terminals // 2) )
          elif pattern == "opposite":
            dest = ( i + 2 ) % terminals
          elif pattern == "neighbor":
            dest = ( i + 1 ) % terminals
          elif pattern == "complement":
            dest = i ^ (terminals-1)
          src = i
          data = Bits32(6)

        if (action == "simulate-1pkt" or action == "verify"):
          src  = packets[0]['src']
          dest = packets[0]['dest']
          data = Bits32(packets[0]['data'])
          packets.pop(0)
          if action == "verify":
            pkt_verify_queue[dest].append(data)

        # inject packet past the warmup period

        timestamp = INVALID_TIMESTAMP
        if ( NUM_WARMUP_CYCLES < ncycles < NUM_SAMPLE_CYCLES ):
          timestamp = ncycles

        if topology == "Ring":
          pkt = PacketType( src, dest, 0, 0, data, timestamp )

        elif topology == "Mesh":
          XYType = mk_bits( clog2( net_width ) )
          timeType = mk_bits(clog2(NUM_SAMPLE_CYCLES+1))
          pkt = PacketType( XYType(src%net_width), XYType(src//net_width),
                  XYType(dest % net_width), XYType(dest//net_width),
                  Bits8(0), data, timeType(timestamp) )

        elif topology == "Torus":
          pkt = PacketType( src % net_width, src // net_width, dest % net_width,
                  dest // net_width, 0, 0, data, timestamp )

        elif topology == "CMesh":
          pkt = PacketType( (src // term_each) %  net_width,
                            (src // term_each) // net_width,
                            (dest // term_each) %  net_width,
                            (dest // term_each) // net_width,
                            dest % term_each,
                            0, data, timestamp )

        elif topology == "Bfly":
          r_dimension = k_ary ** ( n_fly - 1 )
          if r_dimension == 1 or k_ary == 1:
            DstType = mk_bits( n_fly )
          else:
            DstType = mk_bits( clog2( k_ary ) * n_fly )
          bf_dst = DstType(0)
          tmp = 0
          dst = dest
          for index in range( n_fly ):
            tmp = dst // (k_ary**(n_fly-index-1))
            dst = dst %  (k_ary**(n_fly-index-1))
            bf_dst = DstType(bf_dst | DstType(tmp))
            if index != n_fly - 1:
              if k_ary == 1:
                bf_dst = bf_dst * 2
              else:
                bf_dst = bf_dst * k_ary
          pkt = PacketType( src, bf_dst, 0, data, timestamp )

        src_queue[src].append( pkt )
        if ( ncycles < NUM_SAMPLE_CYCLES ):
          packets_generated += 1

        # Inject from source queue

      if ( len( src_queue[i] ) > 0 ):
        if net.recv[i].rdy:
          net.recv[i].msg = src_queue[i][0]
          net.recv[i].en  = Bits1(1)
        else:
          net.recv[i].en  = Bits1(0)
      else:
        net.recv[i].en  = Bits1(0)

      # Receive a packet

      if ( net.send[i].en == 1 ):
        timestamp = int(net.send[i].msg.timestamp)
        all_packets_received += 1
        if action == "verify":
          if net.send[i].msg.payload not in pkt_verify_queue[i]:
            print("x")
            print("[VERIFY FAILED]")
            return

        # collect data for measurement packets
        if ( timestamp != INVALID_TIMESTAMP ):
          total_latency    += ( ncycles - timestamp )
          packets_received += 1
          average_latency = total_latency / float( packets_received )

      # Check if finished - drain phase

      if action == "simulate-lat-vs-bw":
        if ( ncycles >= NUM_SAMPLE_CYCLES and
             all_packets_received >= packets_generated ):
          average_latency = total_latency / float( packets_received )
          sim_done = True
          break
      elif action == "simulate-1pkt" or action == "verify":
        if ( packets_generated > 0 and
             all_packets_received >= packets_generated ):
          sim_done = True
          break

      # Pop the source queue

      if ( net.recv[i].rdy == Bits1(1) ) and ( len( src_queue[i] ) > 0 ):
        src_queue[i].popleft()

    # print line trace if enables
    if action == "simulate-1pkt":
      print( "{:3}:{}".format( ncycles, net.line_trace() ))

    net.tick()
    ncycles += 1

  # FIXME: To extend the period for gtkwave, but does not work yet.
  net.tick()
  net.tick()
  net.tick()

  if action == "verify":
    print("\33[32m.\033[0m", end="")
    sys.stdout.flush()

  # return the calculated average_latency and count of packets received

  return [average_latency, packets_received, ncycles]

#-------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------

from ruamel.yaml import YAML
from pathlib import Path

def main():

  path   = Path('config.yml')
  yaml   = YAML(typ='safe')
  config = yaml.load(path)

  print( config )
  print( "="*74 )

  for action in config['action']:

    if action == 'generate':
      print()
      print( "[GENERATING synthesizable Verilog]" )
      topology = config['network']
      generate( topology, config['terminal'],
                config['dimension'], config['channel_latency'] )
      print( "="*74 )

    if action == 'verify':
      print()
      print( "[VERIFYING using test cases]" )
      terminals = config['terminal']
      for i in range(6):
        packets = [{'src': (0+i)%terminals, 'dest': (terminals-(i+1))%terminals, 'data': 0xffff},
                   {'src': (1+i)%terminals, 'dest': (terminals-(i+2))%terminals, 'data': 0xfffe},
                   {'src': (2+i)%terminals, 'dest': (terminals-(i+3))%terminals, 'data': 0xfffd},
                   {'src': (3+i)%terminals, 'dest': (terminals-(i+4))%terminals, 'data': 0xfffc},
                   {'src': (4+i)%terminals, 'dest': (terminals-(i+5))%terminals, 'data': 0xfffb}]
        topology = config['network']
        verify( topology, config['terminal'], config['dimension'],
                           config['channel_latency'], packets )
      print("\n")
      print( "="*74 )

    if action == 'simulate-1pkt':
      print()
      print( "[SIMULATING single packet]" )
      packets = [{'src': 0, 'dest': config['terminal']-1, 'data': 0xffff},]
      topology = config['network']
      simulate_1pkt( topology, config['terminal'], config['dimension'],
                     config['channel_latency'], packets )
      print( "="*74 )

    if action == 'simulate-lat-vs-bw':
      print()
      print( "[SIMULATING latency vs. bandwidth]" )
      print( "Warmup Cycles:    %d" % NUM_WARMUP_CYCLES )
      print( "Sample Cycles:    %d" % NUM_SAMPLE_CYCLES )
      print( "="*74 )
      print( "|Topology|Pattern    |Inj.Rate|Avg.Lat|Num.Pkt|Cycles|Sim.Time|Speed(c/s)|" )
      print( "|--------|-----------|--------|-------|-------|------|--------|----------|" )

      topology = config['network']

      for pattern in config['pattern']:

        inj             = 0
        avg_lat         = 0
        zero_load_lat   = 0
        running_avg_lat = 0.0
        inj_shamt_mult  = 5
        inj_shamt       = 0.0
        inj_step        = 10

        while inj < 100 and avg_lat <= 100 and avg_lat <= 2.5 * zero_load_lat:

          start_time = time.time()

          # Start simulation

          results = simulate_lat_vs_bw( topology, config['terminal'],
                    config['dimension'], config['channel_latency'],
                    max(inj,1), pattern )

          end_time = time.time()

          avg_lat = results[0]

          print( "|{:<8}|{:<11}|{:<8}|{:<7}|{:<7}|{:<6}|{:<8}|{:<10}|".\
                  format(topology, pattern, max(inj, 1),
                      "{0:.1f}".format(results[0]), results[1], results[2],
                      "{0:.1f}".format(end_time - start_time),
                      "{0:.1f}".format(results[2]/(end_time - start_time))) )

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

      print( "="*74 )
      print()

main()

