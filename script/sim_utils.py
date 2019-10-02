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
import time
from copy import deepcopy
from collections import deque
from dataclasses import dataclass
from random import seed, randint
from pymtl3 import *
from pymtl3.passes.yosys import ImportPass, TranslationPass

seed( 0xfaceb00c )

# Hacky way to add pymtl3-net to path
# TODO: remove this line and use globally installed pymtl3-net
sys.path.insert(0, os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )

from ocn_pclib.ifcs.positions import mk_mesh_pos, mk_ring_pos, mk_bfly_pos
from ocn_pclib.ifcs.packets import mk_mesh_pkt, mk_ring_pkt, mk_cmesh_pkt, mk_bfly_pkt
from ocn_pclib.passes.PassGroups import SimulationPass
from meshnet  import MeshNetworkRTL, MeshNetworkCL
from ringnet  import RingNetworkRTL
from torusnet import TorusNetworkRTL
from cmeshnet import CMeshNetworkRTL
from bflynet  import BflyNetworkRTL

from CLNetWrapper import CLNetWrapper

#-------------------------------------------------------------------------
# module level variable
#-------------------------------------------------------------------------

verbose = False

#-------------------------------------------------------------------------
# convenience variable
#-------------------------------------------------------------------------

_green = '\33[32m'
_reset = '\033[0m'
_red   = '\033[31m'

#-------------------------------------------------------------------------
# Verbose print
#-------------------------------------------------------------------------

def vprint( msg='', value=None ):
  if verbose:
    if value is not None:
      print( msg, value )
    else:
      print( msg )

#-------------------------------------------------------------------------
# add_mesh_arg
#-------------------------------------------------------------------------

def _add_mesh_arg( p ):
  p.add_argument( '--ncols', type=int, default=2, metavar='', help='Number of columns.' )
  p.add_argument( '--nrows', type=int, default=2, metavar='', help='Number of rows.' )
  p.add_argument( '--channel-lat', type=int, default=0,  metavar='', help='Channel latency in cycles. 0 means combinational channel.' )
  p.add_argument( '--channel-bw',  type=int, default=32, metavar='', help='Channel bandwidth in bits.' )

#-------------------------------------------------------------------------
# add_ring_arg
#-------------------------------------------------------------------------

def _add_ring_arg( p ):
  p.add_argument( '--nterminals',  type=int, default=4, metavar='', help='Number of terminals' )
  p.add_argument( '--channel-lat', type=int, default=0,  metavar='', help='Channel latency. 0 means combinational channel.' )
  p.add_argument( '--channel-bw',  type=int, default=32, metavar='', help='Channel bandwidth in bits.' )

#-------------------------------------------------------------------------
# add_torus_arg
#-------------------------------------------------------------------------

def _add_torus_arg( p ):
  p.add_argument( '--ncols', type=int, default=2, metavar='', help='Number of columns.' )
  p.add_argument( '--nrows', type=int, default=2, metavar='', help='Number of rows.' )
  p.add_argument( '--channel-lat', type=int, default=0,  metavar='', help='Channel latency. 0 means combinational channel.' )
  p.add_argument( '--channel-bw',  type=int, default=32, metavar='', help='Channel bandwidth in bits.' )


#-------------------------------------------------------------------------
# add_cmesh_arg
#-------------------------------------------------------------------------

def _add_cmesh_arg( p ):
  p.add_argument( '--ncols', type=int, default=2, metavar='', help='Number of columns.' )
  p.add_argument( '--nrows', type=int, default=2, metavar='', help='Number of rows.' )
  p.add_argument( '--nterminals-each', type=int, default=2, metavar='', help='Number of terminals per router.' )
  p.add_argument( '--channel-lat', type=int, default=0,  metavar='', help='Channel latency. 0 means combinational channel.' )
  p.add_argument( '--channel-bw',  type=int, default=32, metavar='', help='Channel bandwidth in bits.' )

#-------------------------------------------------------------------------
# add_cmesh_arg
#-------------------------------------------------------------------------

def _add_bfly_arg( p ):
  p.add_argument( '--kary', type=int, default=2, metavar='', help='Radix for each router.' )
  p.add_argument( '--nfly', type=int, default=2, metavar='', help='Number of stages.' )
  p.add_argument( '--channel-lat', type=int, default=0,  metavar='', help='Channel latency. 0 means combinational channel.' )
  p.add_argument( '--channel-bw',  type=int, default=32, metavar='', help='Channel bandwidth in bits.' )


#-------------------------------------------------------------------------
# _mk_mesh_net
#-------------------------------------------------------------------------

def _mk_mesh_net( opts ):
  ncols  = opts.ncols
  nrows  = opts.nrows
  nports = opts.ncols * opts.nrows
  payload_nbits = opts.channel_bw
  channel_lat   = opts.channel_lat

  Pos = mk_mesh_pos( ncols, nrows )
  Pkt = mk_mesh_pkt( ncols, nrows, nvcs=1, payload_nbits=payload_nbits )
  if hasattr( opts, 'cl' ) and opts.cl:
    cl_net = MeshNetworkCL( Pkt, Pos, ncols, nrows, channel_lat )
    net    = CLNetWrapper( Pkt, cl_net, nports )
  else:
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
# _mk_torus_net
#-------------------------------------------------------------------------

def _mk_torus_net( opts ):
  ncols = opts.ncols
  nrows = opts.nrows
  payload_nbits = opts.channel_bw
  channel_lat   = opts.channel_lat

  Pos = mk_mesh_pos( ncols, nrows )
  Pkt = mk_mesh_pkt( ncols, nrows, nvcs=2, payload_nbits=payload_nbits )
  net = TorusNetworkRTL( Pkt, Pos, ncols, nrows, channel_lat, nvcs=2, credit_line=2 )
  return net

#-------------------------------------------------------------------------
# _mk_cmesh_net
#-------------------------------------------------------------------------

def _mk_cmesh_net( opts ):
  ncols = opts.ncols
  nrows = opts.nrows
  payload_nbits = opts.channel_bw
  channel_lat   = opts.channel_lat
  router_ninports  = opts.nterminals_each + 4
  router_noutports = opts.nterminals_each + 4

  Pos = mk_mesh_pos( ncols, nrows )
  Pkt = mk_cmesh_pkt( ncols, nrows, router_ninports, router_noutports,
                      nvcs=1, payload_nbits=payload_nbits )
  net = CMeshNetworkRTL( Pkt, Pos, ncols, nrows, opts.nterminals_each, channel_lat )
  return net

#-------------------------------------------------------------------------
# _mk_bfly_net
#-------------------------------------------------------------------------

def _mk_bfly_net( opts ):
  kary = opts.kary
  nfly = opts.nfly
  payload_nbits = opts.channel_bw
  channel_lat   = opts.channel_lat

  Pos = mk_bfly_pos( kary, nfly )
  Pkt = mk_bfly_pkt( kary, nfly, nvcs=1, payload_nbits=payload_nbits )
  net = BflyNetworkRTL( Pkt, Pos, kary, nfly, channel_lat )
  net.set_param( "top.routers*.construct", k_ary=kary )
  net.set_param( "top.routers*.route_units*.construct", n_fly=nfly )

  return net

#-------------------------------------------------------------------------
# _gen_dst_id
#-------------------------------------------------------------------------

def _gen_dst_id( pattern, nports, src_id ):
  if pattern == 'urandom':
    return randint( 0, nports-1 )
  elif pattern == 'partition':
    return randint( 0, nports-1 ) & ( nports//2 - 1 ) | ( src_id & ( nports//2 ) )
  elif pattern == 'opposite':
    return ( src_id + nports//2 ) % nports
  elif pattern == 'neighbor':
    return ( src_id + 1 ) % nports
  elif pattern == 'complement':
    return ( nports-1 ) - src_id
  else:
    raise Exception( f'Unkonwn traffic pattern {pattern}' )

#-------------------------------------------------------------------------
# _gen_mesh_net
#-------------------------------------------------------------------------

def _gen_mesh_pkt( opts, timestamp, src_id ):
  ncols = opts.ncols
  nrows = opts.nrows
  payload_nbits = opts.channel_bw
  nports = ncols * nrows

  x_type = mk_bits( clog2( opts.ncols ) )
  y_type = mk_bits( clog2( opts.nrows ) )

  pkt = mk_mesh_pkt( ncols, nrows, nvcs=1, payload_nbits=payload_nbits )()
  pkt.payload = timestamp

  dst_id    = _gen_dst_id( opts.pattern, nports, src_id )
  pkt.src_x = x_type( src_id %  ncols )
  pkt.src_y = y_type( src_id // ncols )
  pkt.dst_x = x_type( dst_id %  ncols )
  pkt.dst_y = y_type( dst_id // ncols )

  return pkt

#-------------------------------------------------------------------------
# _gen_ring_net
#-------------------------------------------------------------------------

def _gen_ring_pkt( opts, timestamp, src_id ):
  payload_nbits = opts.channel_bw
  nports = opts.nterminals

  id_type = mk_bits( clog2( nports ) )

  pkt = mk_ring_pkt( nports, nvcs=2, payload_nbits=payload_nbits )()
  pkt.payload = timestamp

  dst_id  = _gen_dst_id( opts.pattern, nports, src_id )
  pkt.src = id_type( src_id )
  pkt.dst = id_type( dst_id )

  return pkt

#-------------------------------------------------------------------------
# _gen_torus_net
#-------------------------------------------------------------------------

def _gen_torus_pkt( opts, timestamp, src_id ):
  ncols = opts.ncols
  nrows = opts.nrows
  payload_nbits = opts.channel_bw
  nports = ncols * nrows

  x_type = mk_bits( clog2( opts.ncols ) )
  y_type = mk_bits( clog2( opts.nrows ) )

  pkt = mk_mesh_pkt( ncols, nrows, nvcs=2, payload_nbits=payload_nbits )()
  pkt.payload = timestamp

  dst_id    = _gen_dst_id( opts.pattern, nports, src_id )
  pkt.src_x = x_type( src_id %  ncols )
  pkt.src_y = y_type( src_id // ncols )
  pkt.dst_x = x_type( dst_id %  ncols )
  pkt.dst_y = y_type( dst_id // ncols )
  pkt.vc_id = b1(0)

  return pkt

#-------------------------------------------------------------------------
# _gen_cmesh_net
#-------------------------------------------------------------------------

def _gen_cmesh_pkt( opts, timestamp, src_id ):
  ncols = opts.ncols
  nrows = opts.nrows
  nterminals_each = opts.nterminals_each
  payload_nbits   = opts.channel_bw
  nports          = ncols * nrows * nterminals_each

  router_ninports  = opts.nterminals_each + 4
  router_noutports = opts.nterminals_each + 4

  x_type = mk_bits( clog2( ncols ) )
  y_type = mk_bits( clog2( nrows ) )
  t_type = mk_bits( clog2( nterminals_each ) )

  pkt = mk_cmesh_pkt( ncols, nrows, router_ninports, router_noutports,
                      nvcs=1, payload_nbits=payload_nbits )()
  pkt.payload = timestamp

  dst_id      = _gen_dst_id( opts.pattern, nports, src_id )
  pkt.src_x   = x_type( ( src_id//nterminals_each ) %  ncols )
  pkt.src_y   = y_type( ( src_id//nterminals_each ) // ncols )
  pkt.dst_x   = x_type( ( dst_id//nterminals_each ) %  ncols )
  pkt.dst_y   = y_type( ( src_id//nterminals_each ) // ncols )
  pkt.dst_ter = t_type( dst_id % nterminals_each )

  return pkt

#-------------------------------------------------------------------------
# _gen_bfly_net
#-------------------------------------------------------------------------

def _gen_bfly_pkt( opts, timestamp, src_id ):
  kary          = opts.kary
  nfly          = opts.nfly
  payload_nbits = opts.channel_bw
  nports        = opts.kary ** opts.nfly

  id_type = mk_bits( clog2( nports ) )

  pkt = mk_bfly_pkt( kary, nfly, nvcs=1, payload_nbits=payload_nbits )()
  pkt.payload = timestamp

  dst_id  = _gen_dst_id( opts.pattern, nports, src_id )
  pkt.src = id_type( src_id )
  pkt.dst = id_type( dst_id )

  return pkt

#-------------------------------------------------------------------------
# dictionaries
#-------------------------------------------------------------------------

_net_arg_dict = {
  'mesh'  : _add_mesh_arg,
  'ring'  : _add_ring_arg,
  'torus' : _add_torus_arg,
  'cmesh' : _add_cmesh_arg,
  'bfly'  : _add_bfly_arg,
}

_net_inst_dict = {
  'mesh'  : _mk_mesh_net,
  'ring'  : _mk_ring_net,
  'torus' : _mk_torus_net,
  'cmesh' : _mk_cmesh_net,
  'bfly'  : _mk_bfly_net,
}

_net_nports_dict = {
  'mesh'  : lambda opts: opts.ncols * opts.nrows,
  'ring'  : lambda opts: opts.nterminals,
  'torus' : lambda opts: opts.ncols * opts.nrows,
  'cmesh' : lambda opts: opts.ncols * opts.nrows * opts.nterminals_each,
  'bfly'  : lambda opts: opts.kary ** opts.nfly,
}

_pkt_gen_dict = {
  'mesh'  : _gen_mesh_pkt,
  'ring'  : _gen_ring_pkt,
  'torus' : _gen_torus_pkt,
  'cmesh' : _gen_cmesh_pkt,
  'bfly'  : _gen_bfly_pkt,
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
# SimResult
#-------------------------------------------------------------------------

@dataclass
class SimResult:
  injection_rate : int   = 0
  avg_latency    : float = 0.0
  pkt_generated  : int   = 0
  mpkt_received  : int   = 0
  total_received : int   = 0
  sim_ncycles    : int   = 0
  elapsed_time   : float = 0.0
  timeout        : bool  = False

  def print_result( self ):
    print( f'injection_rate    : {self.injection_rate} %' )
    print( f'average latency   : {self.avg_latency:.2f}'   )
    print( f'simulated cycles  : {self.sim_ncycles}'       )
    print( f'packets generated : {self.total_generated}'   )
    print( f'packets received  : {self.total_received}'    )
    print( f'#measure packets  : {self.mpkt_received}'     )
    print( f'elapsed time      : {self.elapsed_time:.2f} sec'  )

  def to_row( self ):
    return f'| {self.injection_rate:4} | {self.avg_latency:8.2f} | {self.sim_ncycles/self.elapsed_time:5.1f} |'

#-------------------------------------------------------------------------
# net_simulate
#-------------------------------------------------------------------------
# TODO: dump vcd

def net_simulate( topo, opts ):
  if not topo in _net_arg_dict:
    raise Exception( f'Unkonwn network topology {topo}' )

  # Metadata
  nports = get_nports( topo, opts )
  p_type = mk_bits( opts.channel_bw )

  # Instantiate network instance
  vprint( f' - instantiating {topo} with {nports} terminals')
  net = mk_net_inst( topo, opts )

  # Infinite source queues
  src_q = [ deque() for _ in range( nports ) ]

  if opts.dump_vcd:
    vprint( f' - enabling vcd dumping' )
    net.dump_vcd = True
    net.vcd_file_name = f'{topo}-{nports}-{opts.injection_rate}'

  # Elaborating network instance
  vprint( f' - elaborating {topo}' )
  net.elaborate()
  net.apply( SimulationPass )

  vprint( f' - resetting network')
  net.sim_reset()
  net.tick()

  # Constants

  warmup_ncycles   = opts.warmup_ncycles
  measure_npackets = opts.measure_npackets * 2
  timeout_ncycles  = opts.timeout_ncycles


  vprint( f' - simulation starts' )
  vprint( f' - #measure generated / #measure injected / total generated ---- #measure received / total received')

  injection_rate  = opts.injection_rate
  ncycles         = 0
  total_generated = 0
  mpkt_generated  = 0
  mpkt_received   = 0
  total_received  = 0
  total_latency   = 0
  all_received    = 0
  mpkt_injected   = 0

  for i in range( nports ):
    net.send[i].rdy = b1(1) # Always ready

  # Run simulation

  start_time = time.monotonic()

  while True:
    for i in range( nports ):

      # Inject packets to source queue
      if randint(1,100) <= injection_rate:

        # TODO: use number of packets
        # Warmup phase - inject non-measure packet
        if ncycles <= warmup_ncycles:
          # FIXME: we may want to convert ncycles to bits
          pkt = _pkt_gen_dict[ topo ]( opts, p_type(0), i )

        # Sample phase - inject measure packet
        elif mpkt_generated < measure_npackets:
          pkt = _pkt_gen_dict[ topo ]( opts, b32(ncycles), i )
          mpkt_generated += 1

        # Drain phase - just inject
        else:
          pkt = _pkt_gen_dict[ topo ]( opts, p_type(0), i )

        total_generated += 1
        src_q[i].append( pkt )

      # Inject packets from source queue to network
      if len( src_q[i] ) > 0 and net.recv[i].rdy:
        recv_pkt = src_q[i].popleft()
        net.recv[i].msg = recv_pkt
        net.recv[i].en  = b1(1)
        if int(recv_pkt.payload) > 0:
          mpkt_injected += 1
      else:
        net.recv[i].en  = b1(0)

      # Receive packets from network
      if net.send[i].en:
        total_received += 1
        if int(net.send[i].msg.payload) > 0:
          timestamp = int(net.send[i].msg.payload)
          total_latency += ( ncycles - timestamp )
          mpkt_received += 1

      # Check finish

      if mpkt_received >= opts.measure_npackets and mpkt_generated == measure_npackets:
        elapsed_time = time.monotonic() - start_time
        result = SimResult()
        result.injection_rate  = injection_rate
        result.avg_latency     = float( total_latency ) / mpkt_received
        result.total_generated = total_generated
        result.mpkt_received   = mpkt_received
        result.total_received  = total_received
        result.sim_ncycles     = ncycles
        result.elapsed_time    = elapsed_time
        return result

      elif ncycles >= timeout_ncycles:
        elapsed_time = time.monotonic() - start_time
        result = SimResult()
        result.injection_rate  = injection_rate
        result.avg_latency     = float( total_latency ) / mpkt_received
        result.total_generated = total_generated
        result.mpkt_received   = mpkt_received
        result.total_received  = total_received
        result.sim_ncycles     = ncycles
        result.elapsed_time    = elapsed_time
        result.timeout         = True
        vprint( ' - TIMEOUT!' )
        return result

    # Advance simulation

    if opts.trace:
      print( f'{ncycles:3}: {net.line_trace()}' )

    if opts.verbose and ncycles % 100 == 1:
      print( f'{ncycles:4}: gen {mpkt_generated}/{mpkt_injected}/{total_generated} recv {mpkt_received}/{total_received}' )

    net.tick()
    ncycles += 1

#-------------------------------------------------------------------------
# net_simulate_cl
#-------------------------------------------------------------------------

def net_simulate_cl( topo, opts ):
  if not topo in _net_arg_dict:
    raise Exception( f'Unkonwn network topology {topo}' )

  # Metadata
  nports = get_nports( topo, opts )
  p_type = mk_bits( opts.channel_bw )

  # Instantiate network instance
  vprint( f' - instantiating {topo} with {nports} terminals')
  net = mk_net_inst( topo, opts )

  # Infinite source queues
  src_q = [ deque() for _ in range( nports ) ]

  # Elaborating network instance
  vprint( f' - elaborating {topo}' )
  net.elaborate()
  net.apply( SimulationPass )

  vprint( f' - resetting network')
  net.sim_reset()
  net.tick()

  # Constants

  warmup_ncycles   = opts.warmup_ncycles
  measure_npackets = opts.measure_npackets * 2
  timeout_ncycles  = opts.timeout_ncycles

  vprint( f' - simulation starts' )
  vprint( f' - #measure generated / #measure injected / total generated  #measure received / total received')
  injection_rate  = opts.injection_rate
  ncycles         = 0
  total_generated = 0
  mpkt_generated  = 0
  mpkt_received   = 0
  total_received  = 0
  total_latency   = 0
  all_received    = 0
  mpkt_injected   = 0

  # Run simulation

  start_time = time.monotonic()

  while True:
    for i in range( nports ):

      # Inject packets to source queue
      if randint(1,100) <= injection_rate:

        # TODO: use number of packets
        # Warmup phase - inject non-measure packet
        if ncycles <= warmup_ncycles:
          # FIXME: we may want to convert ncycles to bits
          pkt = _pkt_gen_dict[ topo ]( opts, p_type(0), i )

        # Sample phase - inject measure packet
        elif mpkt_generated < measure_npackets:
          pkt = _pkt_gen_dict[ topo ]( opts, b32(ncycles), i )
          mpkt_generated += 1

        # Drain phase - just inject
        else:
          pkt = _pkt_gen_dict[ topo ]( opts, p_type(0), i )

        total_generated += 1
        src_q[i].append( pkt )

      # Inject packets from source queue to network
      if len( src_q[i] ) > 0 and net.recv[i].rdy():
        recv_pkt = src_q[i].popleft()
        net.recv[i]( recv_pkt )
        if int(recv_pkt.payload) > 0:
          mpkt_injected += 1

      # Receive packets from network
      if net.give[i].rdy():
        total_received += 1
        recv_pkt = net.give[i]()
        if int(recv_pkt.payload) > 0:
          timestamp = int(recv_pkt.payload)
          total_latency += ( ncycles - timestamp )
          mpkt_received += 1

      # Check finish

      if mpkt_received >= opts.measure_npackets and mpkt_generated == measure_npackets:
        elapsed_time = time.monotonic() - start_time
        result = SimResult()
        result.injection_rate  = injection_rate
        result.avg_latency     = float( total_latency ) / mpkt_received
        result.total_generated = total_generated
        result.mpkt_received   = mpkt_received
        result.total_received  = total_received
        result.sim_ncycles     = ncycles
        result.elapsed_time    = elapsed_time
        return result

      elif ncycles >= timeout_ncycles:
        elapsed_time = time.monotonic() - start_time
        result = SimResult()
        result.injection_rate  = injection_rate
        result.avg_latency     = float( total_latency ) / mpkt_received
        result.total_generated = total_generated
        result.mpkt_received   = mpkt_received
        result.total_received  = total_received
        result.sim_ncycles     = ncycles
        result.elapsed_time    = elapsed_time
        result.timeout         = True
        vprint( ' - TIMEOUT!' )
        return result

    # Advance simulation

    if opts.trace:
      print( f'{ncycles:3}: {net.line_trace()}' )

    if opts.verbose and ncycles % 100 == 1:
      print( f'{ncycles:4}: gen {mpkt_generated}/{mpkt_injected}/{total_generated} recv {mpkt_received}/{total_received}' )

    net.tick()
    ncycles += 1

#-------------------------------------------------------------------------
# net_simulate_sweep
#-------------------------------------------------------------------------

def net_simulate_sweep( topo, opts ):

  print( f'Topology: {topo} Pattern: {opts.pattern}' )

  result_lst = []

  cur_inj       = 0
  pre_inj       = 0
  cur_avg_lat   = 0.0
  pre_avg_lat   = 0.0
  zero_load_lat = 0.0
  slope         = 0.0
  step          = opts.sweep_step
  threashold    = opts.sweep_threash

  sim_func = net_simulate if not opts.cl else net_simulate_cl

  while cur_avg_lat <= threashold and cur_inj <= 100:
    new_opts = deepcopy( opts )
    new_opts.injection_rate = max( 1, cur_inj )

    vprint()
    vprint( '-'*74 )
    vprint( f'injection_rate : {cur_inj} %' )
    vprint( '-'*74 )
    vprint()

    result = sim_func( topo, new_opts )
    result_lst.append( result )

    if opts.verbose:
      result.print_result()

    cur_avg_lat = result.avg_latency

    if cur_inj == 0:
      zero_load_lat = cur_avg_lat

    else:
      slope = ( cur_avg_lat - pre_avg_lat ) / ( cur_inj - pre_inj )
      if slope >= 1.0:
        step = max( 1, step // 2 )

    pre_inj =  cur_inj
    cur_inj += step
    pre_avg_lat = cur_avg_lat

  # Print table TODO: more informative?

  print()
  print( '+------+----------+-------+' )
  print( '| inj% | avg. lat | speed |' )
  print( '+------+----------+-------+' )

  for r in result_lst:
    print( f'{r.to_row()}' )

  print( '+------+----------+-------+' )

#-------------------------------------------------------------------------
# gen_verilog
#-------------------------------------------------------------------------

def gen_verilog( topo, opts ):
  os.system(f'[ ! -e {topo}.sv ] || rm {topo}.sv')

  vprint( f' - instantiating {topo}')
  net = mk_net_inst( topo, opts )

  vprint( f' - elaborating {topo}')
  net.elaborate()

  vprint( f' - applying translation pass' )
  net.yosys_translate = True
  net.apply( TranslationPass() )

  net_vname = f'{topo[0].upper()}{topo[1:]}'
  os.system(f'mv {net_vname}*.sv {topo}.sv')

#-------------------------------------------------------------------------
# smoke_test
#-------------------------------------------------------------------------

def smoke_test( topo, opts ):
  if not topo in _net_arg_dict:
    raise Exception( f'Unkonwn network topology {topo}' )

  # Metadata
  nports = get_nports( topo, opts )
  p_type = mk_bits( opts.channel_bw )

  # Instantiate network instance
  vprint( f' - instantiating {topo} with {nports} terminals')
  net = mk_net_inst( topo, opts )

  if opts.dump_vcd:
    vprint( f' - enabling vcd dumping' )
    net.dump_vcd = True
    net.vcd_file_name = f'{topo}-{nports}-test'

  # Elaborating network instance
  vprint( f' - elaborating {topo}' )
  net.elaborate()
  net.apply( SimulationPass )

  vprint( f' - resetting network')
  net.sim_reset()
  net.tick()

  vprint( f' - simulation starts' )
  ncycles = 0

  for i in range( nports ):
    net.send[i].rdy = b1(1) # Always ready

  # Inject a packet to port 0
  while not net.recv[0].rdy:
    if opts.trace:
      print( f'{ncycles:3}: {net.line_trace()}' )
    net.tick()
    ncycles += 1

  pkt_opts = deepcopy( opts )
  pkt_opts.pattern = 'complement'
  pkt = _pkt_gen_dict[ topo ]( pkt_opts, p_type(1024), 0 )
  net.recv[0].msg = pkt
  net.recv[0].en  = b1(1)

  # Tick one cycle and stops injecting
  if opts.trace:
    print( f'{ncycles:3}: {net.line_trace()}' )
  net.tick()
  ncycles += 1
  net.recv[0].en = b1(0)

  # Wait until packets arrives
  while not net.send[ nports-1 ].en:
    if opts.trace:
      print( f'{ncycles:3}: {net.line_trace()}' )
    net.tick()
    ncycles += 1

  if net.send[ nports-1 ].msg.payload == p_type(1024):
    print( f' - [{_green}passed{_reset}]' )
  else:
    print( f' - [{_green}FAILED{_reset}]' )
