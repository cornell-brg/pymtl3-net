'''
==========================================================================
common_utils.py
==========================================================================

Author : Yanghui Ou
  Date : Jan 13, 2020
'''
import sys
import os
import subprocess
import math
from dataclasses import dataclass
from pymtl3 import *
from pymtl3.stdlib.test.test_srcs import TestSrcRTL
from ocn_pclib.ifcs.packets import mk_ring_pkt
from ocn_pclib.ifcs.positions import mk_ring_pos
from ocn_pclib.test.net_sinks import TestNetSinkRTL
from ocn_pclib.test import run_sim

from ringnet import RingNetworkRTL
from ringnet.RingNetworkFL import ringnet_fl

#-------------------------------------------------------------------------
# run_cmd
#-------------------------------------------------------------------------

def run_cmd( cmd ):
  print( f' - executing: {cmd}' )

  try:
    result = subprocess.check_output( cmd, shell=True ).strip()

  except subprocess.CalledProcessError as e:
    print( f'\nERROR running the following command:\n{e.cmd}\n' )
    print( f'{e.output}' )
    exit(1)

  print( f'{result.decode( "utf-8" )}' )
  return result.decode( 'utf-8' )

#-------------------------------------------------------------------------
# avg_complexity
#-------------------------------------------------------------------------

def avg_complexity( lst ):
  total = 0.0
  for pkt in lst:
    total += ( pkt.src.uint() + pkt.dst.uint() + pkt.payload[0:8].uint() +pkt.payload[8:16].uint() ) / 4.0
  return total / float( len(lst) )

#-------------------------------------------------------------------------
# TestReport
#-------------------------------------------------------------------------

@dataclass
class TestReport:
  ntests     : int  = None
  ntrans     : int  = None
  nterminals : int  = None
  complexity : int  = None
  failed     : bool = None

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
# NOTE: To avoid saturating the network, assign a random delay to test
# source based on the number of terminals.

class RingTestHarness( Component ):

  def construct( s, PktType, nterminals, src_pkts, sink_pkts ):

    RingPos = mk_ring_pos( nterminals )
    cmp_fn  = lambda a, b: a.payload == b.payload

    # Calculate random injection rate
    min_delay = 0
    max_delay = 1
    if nterminals >= 8:
      inj_rate = 8.0 / nterminals
      min_delay = int( math.ceil( 1.0 / inj_rate ) )
      max_delay = min_delay + 1

    s.srcs  = [ TestSrcRTL( PktType, src_pkts[i], interval_delay=max_delay ) for i in range(nterminals) ]
    s.dut   = RingNetworkRTL( PktType, RingPos, nterminals )
    s.sinks = [ TestNetSinkRTL( PktType, sink_pkts[i], match_func=cmp_fn )
                for i in range(nterminals) ]

    for i in range( nterminals ):
      s.srcs[i].send //= s.dut.recv[i]
      s.dut.send[i]  //= s.sinks[i].recv

  def done( s ):
    srcs_done  = True
    sinks_done = True
    for src, sink in zip( s.srcs, s.sinks ):
      srcs_done  = srcs_done and src.done()
      sinks_done = sinks_done and sink.done()
    return srcs_done and sinks_done

  def line_trace( s ):
    return s.dut.line_trace()

#-------------------------------------------------------------------------
# mk_src_pkts
#-------------------------------------------------------------------------

def mk_src_pkts( nterminals, lst ):
  src_pkts = [ [] for _ in range(nterminals) ]
  for pkt in lst:
    src_pkts[ pkt.src.uint() ].append( pkt )
  return src_pkts

#-------------------------------------------------------------------------
# run_test_case
#-------------------------------------------------------------------------

def run_test_case( nterminals, test_seq, max_cycles=1000, translate='', trace=False ):
  PktType  = mk_ring_pkt( nterminals )
  src_pkts = mk_src_pkts( nterminals, test_seq )
  dst_pkts = ringnet_fl( src_pkts )

  th = RingTestHarness( PktType, nterminals, src_pkts, dst_pkts )
  run_sim( th, max_cycles, translate, trace )
