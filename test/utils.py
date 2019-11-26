'''
==========================================================================
 utils.py
==========================================================================
Helper stuff for the run_test script.

Author : Yanghui Ou
  Date : Nov 22, 2019

'''
import sys
import os
import math
import subprocess
import random
from collections import deque
from dataclasses import dataclass
from pymtl3      import *

# Hacky way to add the project root directory to path
sys.path.insert( 0, os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )

import hypothesis
import hypothesis.strategies as st

from ringnet.RingNetworkRTL       import RingNetworkRTL
from ringnet.RingNetworkFL        import ringnet_fl
from ocn_pclib.ifcs.packets       import mk_ring_pkt
from ocn_pclib.ifcs.positions     import mk_ring_pos
from pymtl3.stdlib.test.test_srcs import TestSrcRTL
from ocn_pclib.test.net_sinks     import TestNetSinkRTL


#-------------------------------------------------------------------------
# TestFailed
#-------------------------------------------------------------------------

class TestFailed( Exception ):
  ...

#-------------------------------------------------------------------------
# run_cmd
#-------------------------------------------------------------------------

def run_cmd( cmd ):
  print( f' - executinig: {cmd}' )

  try:
    result = subprocess.check_output( cmd, shell=True ).strip()

  except subprocess.CalledProcessError as e:
    print( f'\nERROR running the following command:\n{e.cmd}\n' )
    print( f'{e.output}' )
    exit(1)

  print( f'{result.decode("utf-8")}' )
  return result

#-------------------------------------------------------------------------
# TestReport
#-------------------------------------------------------------------------
# A dataclass to record useful data

@dataclass
class TestReport:
  num_test_cases : int  = None
  error_msg      : str  = None
  ntrans         : int  = None
  nrouters       : int  = None
  failed         : bool = True

#  def avg_magnitude( self ):
#    acc = 0.0
#    for c in self.seq:
#      acc += math.sqrt( c.real ** 2 + c.imag ** 2 )
#    return acc / len( self.seq )

#-------------------------------------------------------------------------
# TestHarness()
#-------------------------------------------------------------------------
# Test harness for ring topology

class TestHarness( Component ):

  def construct( s, MsgType, nrouters, src_msgs, sink_msgs ):

    s.nrouters = nrouters
    RingPos = mk_ring_pos( nrouters )

    match_func = lambda a, b : (a.payload == b.payload and
                 a.src == b.src and a.dst == b.dst)

    s.srcs  = [ TestSrcRTL( MsgType, src_msgs[i] )
              for i in range( nrouters ) ]

    s.dut   = RingNetworkRTL( MsgType, RingPos, nrouters, 0)

    s.sinks = [ TestNetSinkRTL( MsgType, sink_msgs[i],
              match_func = match_func )
              for i in range( nrouters ) ]

    # Connections
    for i in range ( s.dut.num_routers ):

      s.srcs[i].send //= s.dut.recv[i]
      s.dut.send[i]  //= s.sinks[i].recv

  def done( s ):

    srcs_done = True
    sinks_done = True

    for i in range( s.nrouters ):
      srcs_done = srcs_done and s.srcs[i].done()
      sinks_done = sinks_done and s.sinks[i].done()

    return srcs_done and sinks_done

  def line_trace( s ):

    return s.dut.line_trace()

#-------------------------------------------------------------------------
# mk_src_pkts
#-------------------------------------------------------------------------

def mk_src_pkts( nrouters, lst ):
  src_pkts = [ [] for _ in range( nrouters ) ]
  src = 0
  for pkt in lst:
    src = pkt.src
    src_pkts[ src ].append( pkt )

  return src_pkts

#-------------------------------------------------------------------------
# do_test
#-------------------------------------------------------------------------

def do_test( nrouters, trace_size, trace=False ):

  global failed

  PktType = Pkt = mk_ring_pkt( nrouters )
  src_pkts = [ [] for _ in range( nrouters ) ]

  for _ in range( trace_size ):
    src = random.randint( 0, nrouters - 1 )
    dst = random.randint( 0, nrouters - 1 )
    data = random.randint( 0, 65535 )
    pkt = PktType( src, dst, 0, 0, data )
    src_pkts[ src ].append( pkt )

  dst_pkts = ringnet_fl( src_pkts )
  dut = TestHarness( PktType, nrouters, src_pkts, dst_pkts )

  dut.elaborate()

  dut.apply( SimulationPass )
  dut.sim_reset()

  # Run simulation
  max_cycles = trace_size + 2 * nrouters
  ncycles = 0

  if trace:
    print()
    print( "{:3}:{}".format( ncycles, dut.line_trace() ))

  while not dut.done() and ncycles < max_cycles:
    dut.tick()
    ncycles += 1
    if trace:
      print( "{:3}:{}".format( ncycles, dut.line_trace() ))

  # Check timeout
  if ncycles >= max_cycles:
    print( "cheng... failed in time checking..." )
    failed = True
    raise TestFailed( f'Failed with {trace_size} transactions' )

#-------------------------------------------------------------------------
# run_random_test
#-------------------------------------------------------------------------

def run_random_test( opts ):

  for i in range( opts.max_examples ):

    nrouters = random.randint( 2, 16 )
    ntrans   = random.randint( 1, 100 )

    if opts.verbose:
      print()
      print( '-'*74 )
      print( f' test case #{i+1}' )
      print( '-'*74 )
      print( f' - nrouters    = {nrouters}' )
      print( f' - ntrans      = {ntrans}' )

    try:
      do_test( nrouters, ntrans, opts.trace )

    except TestFailed as e:

      rpt = TestReport(
        num_test_cases = i+1,
        error_msg      = f'{e}',
        ntrans         = ntrans,
        nrouters       = nrouters,
      )

      if opts.verbose:
        print( f'{e}' )

      return rpt

  return TestReport( num_test_cases = opts.max_examples, failed = False )

#-------------------------------------------------------------------------
# run_iter_test
#-------------------------------------------------------------------------

def run_iter_test( opts ):

  tests_per_step = opts.tests_per_step

  test_idx = 1

  for nrouters in range( 8, 64, 8 ):

    for ntrans in range( tests_per_step, 10 * tests_per_step, tests_per_step ):

       if opts.verbose:
         print()
         print( '-'*74 )
         print( f' test case #{test_idx}' )
         print( '-'*74 )
         print( f' - nrouters   = {nrouters}' )
         print( f' - ntrans     = {ntrans}' )

       try:
         do_test( nrouters, ntrans, opts.trace )
         test_idx += 1

       except TestFailed as e:

         rpt = TestReport(
           num_test_cases = test_idx,
           error_msg      = f'{e}',
           ntrans         = ntrans,
           nrouters       = nrouters,
         )

         if opts.verbose:
           print( f'{e}' )

         return rpt

  return TestReport( num_test_cases = test_idx, failed = False )

#-------------------------------------------------------------------------
# global variable for hypothesis
#-------------------------------------------------------------------------
# Hacky

test_idx = 1
failed   = False
rpt      = TestReport()

#-------------------------------------------------------------------------
# run_hypothesis_test
#-------------------------------------------------------------------------

def run_hypothesis_test( opts ):
  # Generate a hypothesis test

  @hypothesis.settings( deadline = None, max_examples = opts.max_examples )
  @hypothesis.given(
#    nrouters   = st.integers( 2, 64  ),
    hypothesis_nrouters   = st.data(),
    ntrans                = st.integers( 1, 100 )
  )
  def _run( hypothesis_nrouters, ntrans ):
    global test_idx
    global failed
    global rpt

#    x = seq.draw( sequence_strat( complex_t, N, min_value, max_value ) )
#    x = [ c.to_complex() for c in x ]
    nrouters = hypothesis_nrouters.draw(st.integers(min_value=2, max_value=64))

    if opts.verbose:
      print()
      print( '-'*74 )

      if not failed:
        print( f' test case #{test_idx}' )
      else:
        print( ' shrinking...' )

      print( '-'*74 )
      print( f' - nrouters   = {nrouters}' )
      print( f' - ntrans     = {ntrans}' )

    # Exploring phase

    if not failed:
      test_idx += 1

    # Shrinking phase - record data

    else:
      rpt = TestReport(
        num_test_cases = test_idx,
        error_msg      = f'hypothesis error',
        ntrans         = ntrans,
        nrouters       = nrouters,
      )

    do_test( nrouters, ntrans, opts.trace )

  try:
    _run()
    return TestReport( num_test_cases = test_idx, failed = False )

  except TestFailed as e:
    rpt.error_msg = f'{e}'
    return rpt
