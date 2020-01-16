'''
==========================================================================
pyh2_utils.py
==========================================================================
Utilities for pyh2 test.

Author : Yanghui Ou
  Date : Jan 14, 2020
'''
import hypothesis
from hypothesis import strategies as st
from pymtl3 import *
from ocn_pclib.ifcs.packets import mk_ring_pkt
from ringnet import RingNetworkRTL
from ringnet.RingNetworkFL import ringnet_fl
from common_utils import TestReport, RingTestHarness, mk_src_pkts, avg_complexity

#-------------------------------------------------------------------------
# global variable for hypothesis
#-------------------------------------------------------------------------

test_idx      = 0
failed_global = False
rpt           = TestReport()

#-------------------------------------------------------------------------
# reset_global
#-------------------------------------------------------------------------

def reset_global():
  global test_idx, failed_global, rpt
  test_idx      = 0
  failed_global = False
  rpt           = TestReport()

#-------------------------------------------------------------------------
# PyH2TestFailed
#-------------------------------------------------------------------------

class PyH2TestFailed( Exception ):
  ...

#-------------------------------------------------------------------------
# ring_pkt_strat
#-------------------------------------------------------------------------

@st.composite
def ring_pkt_strat( draw, nterminals ):
  PktType = mk_ring_pkt( nterminals )
  src     = draw( st.integers(0, nterminals-1) )
  dst     = draw( st.integers(0, nterminals-1) )
  payload = draw( st.integers(0, 256) )
  return PktType( src=src, dst=dst, payload=payload )


#-------------------------------------------------------------------------
# run_pyh2_sim
#-------------------------------------------------------------------------

def run_sim( th, max_cycles=1000, translation='', trace=True ):
  global failed_global
  th.elaborate()

  if translation == 'sverilog':
    TransImport = SVTransImport
    th.dut.sverilog_translate_import = True
    th.dut.config_sverilog_import = SVConfig(
      vl_trace = True,
    )

  elif translation == 'yosys':
    TransImport = YSTransImport
    th.dut.yosys_translate_import = True
    th.dut.config_yosys_import = SVConfig(
      vl_trace = True,
    )

  if translation:
    th = TransImport()( th )
    th.elaborate()

  th.apply( SimulationPass() )

  failed_local = False
  try:
    th.sim_reset()
  except:
    failed_global = True
    failed_local  = True

  # Run simulation
  ncycles = 0

  if trace:
    print()
    print( "{:3}:{}".format( ncycles, th.line_trace() ))

  while not th.done() and ncycles < max_cycles:
    try:
      th.tick()
    except:
      failed_global = True
      failed_local  = True
      break

    ncycles += 1
    if trace: print( "{:3}:{}".format( ncycles, th.line_trace() ))

  # Check timeout
  if failed_local or ncycles >= max_cycles:
    failed_global = True
    raise PyH2TestFailed( 'test failed!' )

  # if ncycles >= max_cycles:
  #   failed_global = True
  #   raise PyH2TestFailed( 'time out!' )

#-------------------------------------------------------------------------
# run_test_case
#-------------------------------------------------------------------------

def run_test_case( nterminals, test_seq, max_cycles=1000, translate='', trace=False ):
  PktType  = mk_ring_pkt( nterminals )
  src_pkts = mk_src_pkts( nterminals, test_seq )
  dst_pkts = ringnet_fl( src_pkts )

  th = RingTestHarness( PktType, nterminals, src_pkts, dst_pkts )
  run_sim( th, max_cycles, translate, trace )

#-------------------------------------------------------------------------
# run_pyh2
#-------------------------------------------------------------------------
# TODO: Reset global variables before return

def run_pyh2( opts ):
  global test_idx
  global failed_global
  global rpt

  min_nterminals = 2
  max_nterminals = opts.max_nterminals
  min_ntrans     = 1
  max_ntrans     = opts.max_ntrans

  @hypothesis.settings( deadline=None, max_examples=opts.max_examples )
  @hypothesis.given(
    nterminals = st.integers( min_nterminals, max_nterminals ),
    seq        = st.data(),
  )
  def _run_pyh2( nterminals, seq ):
    global test_idx
    global failed_global
    global rpt
    test_seq = seq.draw( st.lists( ring_pkt_strat( nterminals ),
                         min_size=min_ntrans, max_size=max_ntrans ) )
    ntrans   = len( test_seq )
    hypothesis.target( len(test_seq)*1.0 )

    # Generate phase
    if not failed_global:
      test_idx += 1

    # Shrinking phase
    else:
      rpt = TestReport(
        ntests     = test_idx,
        ntrans     = ntrans,
        nterminals = nterminals,
        complexity = avg_complexity( test_seq ),
        failed     = True,
      )

    if opts.verbose:
      print()
      print( '-'*74 )

      if not failed_global:
        print( f'pyh2 #{test_idx}' )
      else:
        print( ' pyh2 shrinking...')

      print( '-'*74 )
      print( f'  + nterminals: {nterminals}' )
      print( f'  + ntransactions: {ntrans}' )
      print( f'  + test sequence:' )
      print( '    ' + '\n    '.join([ str(p) for p in test_seq]) )

    run_test_case( nterminals, test_seq, ntrans*50 )

  try:
    _run_pyh2()
    return TestReport( ntests=test_idx, failed=False )

  except PyH2TestFailed as e:
    return rpt
