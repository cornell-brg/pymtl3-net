"""
==========================================================================
utils.py
==========================================================================
Utility functions for pyocn script.

Author: Yanghui Ou
  Date: Sep 24, 2019
"""

import sys
import os
import argparse
import subprocess
from copy import deepcopy
from collections import deque
from dataclasses import dataclass
from random import seed, randint
from pymtl3 import *

seed( 0xfaceb00c )

# Hacky way to add pymtl3-net to path
# TODO: remove this line and use globally installed pymtl3-net
sys.path.insert(0, os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )

from ocn_pclib.ifcs.positions import mk_mesh_pos, mk_ring_pos, mk_bfly_pos
from meshnet import MeshNetworkRTL
from ringnet import RingNetworkRTL

from measure_packets import mk_mesh_pkt, mk_ring_pkt

#-------------------------------------------------------------------------
# module level variable
#-------------------------------------------------------------------------

verbose = False
warmup_ncycles = 500
sample_ncycles = 500 + warmup_ncycles

#-------------------------------------------------------------------------
# Verbose print
#-------------------------------------------------------------------------

def vprint( msg, value=None ):
  if verbose:
    if value is not None:
      print( msg, value )
    else:
      print( msg )

#-------------------------------------------------------------------------
# add_mesh_arg
#-------------------------------------------------------------------------

def _add_mesh_arg( p ):
  p.add_argument( '--ncols', type=int, default=2, metavar='' )
  p.add_argument( '--nrows', type=int, default=2, metavar='' )
  p.add_argument( '--channel-lat', type=int, default=0, metavar='' )
  p.add_argument( '--channel-bw',  type=int, default=32, metavar='' )

#-------------------------------------------------------------------------
# add_ring_arg
#-------------------------------------------------------------------------

def _add_ring_arg( p ):
  p.add_argument( '--nterminals',  type=int, default=4, metavar='' )
  p.add_argument( '--channel-lat', type=int, default=0, metavar='' )
  p.add_argument( '--channel-bw',  type=int, default=32, metavar='' )

#-------------------------------------------------------------------------
# _mk_mesh_net
#-------------------------------------------------------------------------

def _mk_mesh_net( opts ):
  ncols = opts.ncols
  nrows = opts.nrows
  payload_nbits = opts.channel_bw
  channel_lat   = opts.channel_lat

  Pos = mk_mesh_pos( ncols, nrows )
  Pkt = mk_mesh_pkt( ncols, nrows, nvcs=1, payload_nbits=payload_nbits )
  net = MeshNetworkRTL( Pkt, Pos, ncols, nrows, channel_lat )
  return net

#-------------------------------------------------------------------------
# _mk_ring_net
#-------------------------------------------------------------------------

def _mk_ring_net( opts ):
  nterminals = opts.nterminals
  payload_nbits = opts.channel_bw
  channel_lat   = opts.channel_lat

  Pos = mk_ring_pos( nterminals )
  Pkt = mk_ring_pkt( nterminals, nvcs=2, payload_nbits=payload_nbits )
  net = RingNetworkRTL( Pkt, Pos, nterminals, channel_lat, nvcs=2, credit_line=2 )
  return net

#-------------------------------------------------------------------------
# _gen_mesh_net
#-------------------------------------------------------------------------

def _gen_mesh_pkt( opts, timestamp, measure ):
  ncols = opts.ncols
  nrows = opts.nrows
  payload_nbits = opts.channel_bw
  nports = ncols * nrows

  x_type = mk_bits( clog2( opts.ncols ) )
  y_type = mk_bits( clog2( opts.nrows ) )

  pkt = mk_mesh_pkt( ncols, nrows, nvcs=1, payload_nbits=payload_nbits )()
  pkt.payload = timestamp
  pkt.measure = measure
  if opts.pattern == 'urandom':
    dst_id    = randint( 0, nports-1 )
    pkt.dst_x = x_type( dst_id %  ncols )
    pkt.dst_y = y_type( dst_id // ncols )
  else:
    raise Exception( f'Unkonwn traffic pattern {opts.pattern}' )

  return deepcopy( pkt )

#-------------------------------------------------------------------------
# _gen_ring_net
#-------------------------------------------------------------------------

def _gen_ring_pkt( opts, timestamp, measure ):
  payload_nbits = opts.channel_bw
  nports = opts.nterminals

  id_type = mk_bits( clog2( nports ) )

  pkt = mk_ring_pkt( nports, nvcs=2, payload_nbits=payload_nbits )()
  pkt.payload = timestamp
  pkt.measure = measure
  if opts.pattern == 'urandom':
    pkt.dst = id_type( randint( 0, nports-1 ) )
  else:
    raise Exception( f'Unkonwn traffic pattern {opts.pattern}' )

  return deepcopy( pkt )

#-------------------------------------------------------------------------
# dictionaries
#-------------------------------------------------------------------------

_net_arg_dict = {
  'mesh' : _add_mesh_arg,
  'ring' : _add_ring_arg,
}

_net_inst_dict = {
  'mesh' : _mk_mesh_net,
  'ring' : _mk_ring_net,
}

_net_nports_dict = {
  'mesh' : lambda opts: opts.ncols * opts.nrows,
  'ring' : lambda opts: opts.nterminals,
}

_pkt_gen_dict = {
  'mesh' : _gen_mesh_pkt,
  'ring' : _gen_ring_pkt,
}

#-------------------------------------------------------------------------
# mk_net_arg_parser
#-------------------------------------------------------------------------

def mk_net_arg_parser( topo ):
  if not topo in _net_arg_dict:
    raise Exception( f'Unkonwn network topology {topo}' )

  p = argparse.ArgumentParser(
    # description = f'{topo}',
    usage = f'./pyocn sim {topo} [<flags>]',
  )
  _net_arg_dict[ topo ]( p )
  return p

#-------------------------------------------------------------------------
# mk_net_inst
#-------------------------------------------------------------------------

def mk_net_inst( topo, opts ):
  if not topo in _net_arg_dict:
    raise Exception( f'Unkonwn network topology {topo}' )
  return _net_inst_dict[ topo ]( opts )

#-------------------------------------------------------------------------
# get_nports
#-------------------------------------------------------------------------

def get_nports( topo,  opts ):
  if not topo in _net_arg_dict:
    raise Exception( f'Unkonwn network topology {topo}' )
  return _net_nports_dict[ topo ]( opts )

#-------------------------------------------------------------------------
# net_simulate
#-------------------------------------------------------------------------
# TODO: dump vcd

@dataclass
class SimResult:
  avg_latency    : float = 0.0
  mpkt_generated : int = 0
  mpkt_received  : int = 0
  total_generated: int = 0
  total_received : int = 0
  sim_ncycles    : int = 0

def net_simulate( topo, opts ):
  if not topo in _net_arg_dict:
    raise Exception( f'Unkonwn network topology {topo}' )

  # Instantiate network instance
  vprint( f' - instantiating {topo}')
  net = mk_net_inst( topo, opts )

  # Metadata
  nports = get_nports( topo, opts )

  # Infinite source queues
  src_q = [ deque() for _ in range( nports ) ]

  # Elaborating network instance
  vprint( f' - elaborating {topo}' )
  net.elaborate()
  net.apply( SimulationPass )
  vprint( f' - resetting network')
  net.sim_reset()

  # Run simulation

  vprint( f' - simulation starts' )
  injection_rate  = opts.injection_rate
  ncycles         = 0
  mpkt_generated  = 0
  mpkt_received   = 0
  total_generated = 0
  total_received  = 0
  total_latency   = 0
  for i in range( nports ):
    net.send[i].rdy = b1(1) # Always ready
    net.recv[i].msg = net.recv[i].MsgType()

  while True:
    for i in range( nports ):

      # Inject packets to source queue
      if randint(1,100) <= injection_rate:
        total_generated += 1

        # Warmup or drain phase - inject non-measure packet
        if ncycles <= warmup_ncycles or ncycles >= sample_ncycles:
          # FIXME: we may want to convert ncycles to bits
          pkt = _pkt_gen_dict[ topo ]( opts, b32(0), measure=b1(0) )
          src_q[i].append( pkt )

        # Sample phase - inject measure packet
        else:
          pkt = _pkt_gen_dict[ topo ]( opts, b32(ncycles), measure=b1(1) )
          src_q[i].append( pkt )
          mpkt_generated += 1

      # Inject packets from source queue to network
      if len( src_q[i] ) > 0 and net.recv[i].rdy:
        recv_pkt = src_q[i].popleft()
        net.recv[i].msg = recv_pkt
        net.recv[i].en  = b1(1)
      else:
        net.recv[i].en  = b1(0)

      # Receive packets from network
      if net.send[i].en:
        total_received += 1
        # if net.send[i].msg.measure:
        if int(net.send[i].msg.payload) > 0:
          # vprint( f'{i} received')
          timestamp = int(net.send[i].msg.payload)
          total_latency += ( ncycles - timestamp )
          mpkt_received += 1

      # Check finish

      if ncycles >= sample_ncycles and mpkt_received >= mpkt_generated-20:
        result = SimResult()
        result.avg_latency     = float( total_latency ) / mpkt_received
        result.mpkt_generated  = mpkt_generated
        result.mpkt_received   = mpkt_received
        result.total_generated = total_generated
        result.total_received  = total_received
        result.sim_ncycles     = ncycles
        return result

      # Advance simulation

      if opts.trace:
        print( f'{ncycles:3}: {net.line_trace()}' )

      if opts.verbose and ncycles % 100 == 1:
        print( f'{ncycles:4}: gen {mpkt_generated}/{total_generated} recv {mpkt_received}/{total_received}' )

      net.tick()
      ncycles += 1
