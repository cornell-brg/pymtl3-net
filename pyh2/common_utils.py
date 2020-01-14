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

class RingTestHarness( Component ):

  def construct( PktType, nterminals, src_pkts, sink_pkts ):

    RingPos = mk_ring_pos( nterminals )
    cmp_fn  = lambda a, b: a.payload == b.payload

    s.srcs  = [ TestSrcRTL( PktType, src_pkts[i] ) for i in range(nterminals) ]
    s.dut   = RingNetworkRTL( PktType, RingPos, nterminals, 0 )
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
        sinks_done = sinks_done and sinks_done()
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
  src_pkts = mk_src_pkts( test_seq )
  dst_pkts = ringnet_fl( src_pkts )

  th = TestHarness( PktType, nterminals, src_pkts, sink_pkts )
  run_sim( th, max_cycles, translate, trace )
