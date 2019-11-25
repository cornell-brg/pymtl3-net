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
from dataclasses import dataclass
#from numpy.fft import fft

# Hacky way to add the project root directory to path
sys.path.insert( 0, os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )

from pymtl3 import *
from ringnet.RingNetworkRTL   import RingNetworkRTL
from ocn_pclib.ifcs.packets   import mk_ring_pkt
from ocn_pclib.ifcs.positions import mk_ring_pos
#from fft_gen.utils import *
#from fft_gen.FFTUnit import FFTUnit
#from datatypes.complex_fixed import mk_complex_fixed

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
  seq            : list = None
  N              : int  = None
  frac_nbits     : int  = None
  int_nbits      : int  = None
  failed         : bool = True

  def avg_magnitude( self ):
    acc = 0.0
    for c in self.seq:
      acc += math.sqrt( c.real ** 2 + c.imag ** 2 )
    return acc / len( self.seq )

#-------------------------------------------------------------------------
# do_test
#-------------------------------------------------------------------------
# x needs to be a list of complex numbers rather than complex fixed
# objects

#def do_test( Type, N, x, trace=False ):
def do_test():
  MsgType = Pkt = mk_ring_pkt( 4 )
  RingPos = mk_ring_pos( 4 )
  dut = RingNetworkRTL( MsgType, RingPos, 4, 0)

  pkt = MsgType( 0, 2, 0, 0, 0 )
  src_queue = []
  dst_queue = []
  src_queue.append( pkt )

  try:
    dut.elaborate()

  except:
    if trace:
      print( ' - elaboration failed! skipping test!' )
    return

  dut.apply( SimulationPass )
  dut.sim_reset()

  for i in range( 4 ):
    dut.send[i].rdy = 1

  dut.tick()

  if len( src_queue ) > 0:
    if dut.recv[0].rdy:
      dut.recv[0].msg = src_queue[0]
      dut.recv[0].en = 1
      print( "enabled~!" )
    else:
      dut.recv[0].en = 0
  else:
    model.recv[i].en = 0

  while len( dst_queue ) < 1:
    if dut.send[2].en == 1:
      print( "I got it...." )
      msg = dut.send[2].msg
      dst_queue.append( msg )

    dut.tick()

  print( "cheng: can exit..." )
  exit()

#  dut_in = mk_fft_in( Type, x )
#  set_fft_in( dut, dut_in )
#  dut.tick()
#
#  if trace:
#    print( dut.line_trace() )
#
#  res = get_fft_out( dut )
#
#  ref = fft( x )
#
#  for a, b in zip( res, ref ):
#    if not almost_equal( a, b ):
#      err_msg = f'''\
# - Test failed!
# - x   = {x}
# - ref = {ref}
# - {a} != {b}
#'''
#      raise TestFailed( err_msg )

#-------------------------------------------------------------------------
# run_random_test
#-------------------------------------------------------------------------

def run_random_test( opts ):

  min_frac_nbits = opts.min_frac_nbits
  max_frac_nbits = opts.max_frac_nbits
  min_int_nbits  = opts.min_int_nbits
  max_int_nbits  = opts.max_int_nbits
  min_exp        = clog2( opts.min_N )
  max_exp        = clog2( opts.max_N )

  for i in range( opts.max_examples ):

    frac_nbits = random.randint( min_frac_nbits, max_frac_nbits )
    int_nbits  = random.randint( min_int_nbits,  max_int_nbits  )
    nbits      = int_nbits + frac_nbits
    N          = 2 ** random.randint( min_exp, max_exp )
#    complex_t  = mk_complex_fixed( nbits, frac_nbits )
    min_value  = opts.min_value
    max_value  = opts.max_value
    do_test()
#    x = rand_sequence( complex_t, N, min_value, max_value )
#
#    if opts.verbose:
#      print()
#      print( '-'*74 )
#      print( f' test case #{i+1}' )
#      print( '-'*74 )
#      print( f' - frac_nbits = {frac_nbits}' )
#      print( f' - int_nbits  = {int_nbits}' )
#      print( f' - N          = {N}' )
#      print( f' - x          = {x}' )
#
#    try:
#      do_test( complex_t, N, x, opts.trace )
#
#    except TestFailed as e:
#
#      rpt = TestReport(
#        num_test_cases = i+1,
#        error_msg      = f'{e}',
#        seq            = x,
#        N              = N,
#        frac_nbits     = frac_nbits,
#        int_nbits      = int_nbits,
#      )
#
#      if opts.verbose:
#        print( f'{e}' )
#
#      return rpt
#
#  return TestReport( num_test_cases = opts.max_examples, failed = False )
#
##-------------------------------------------------------------------------
## run_iter_test
##-------------------------------------------------------------------------
#
#def run_iter_test( opts ):
#
#  min_frac_nbits = opts.min_frac_nbits
#  max_frac_nbits = opts.max_frac_nbits
#  min_int_nbits  = opts.min_int_nbits
#  max_int_nbits  = opts.max_int_nbits
#  min_exp        = clog2( opts.min_N )
#  max_exp        = clog2( opts.max_N )
#  tests_per_step = opts.tests_per_step
#
#  test_idx = 1
#
#  for exp in range( min_exp, max_exp ):
#    for frac_nbits in range( min_frac_nbits, max_frac_nbits ):
#      for int_nbits in range( min_int_nbits, max_int_nbits ):
#        for _ in range( tests_per_step ):
#
#          nbits     = int_nbits + frac_nbits
#          N         = 2 ** exp
#          complex_t = mk_complex_fixed( nbits, frac_nbits )
#          min_value = opts.min_value
#          max_value = opts.max_value
#
#          x = rand_sequence( complex_t, N, min_value, max_value )
#
#          if opts.verbose:
#            print()
#            print( '-'*74 )
#            print( f' test case #{test_idx}' )
#            print( '-'*74 )
#            print( f' - frac_nbits = {frac_nbits}' )
#            print( f' - int_nbits  = {int_nbits}' )
#            print( f' - N          = {N}' )
#            print( f' - x          = {x}' )
#
#          try:
#            do_test( complex_t, N, x, opts.trace )
#            test_idx += 1
#
#          except TestFailed as e:
#
#            rpt = TestReport(
#              num_test_cases = test_idx,
#              error_msg      = f'{e}',
#              seq            = x,
#              N              = N,
#              frac_nbits     = frac_nbits,
#              int_nbits      = int_nbits,
#            )
#
#            if opts.verbose:
#              print( f'{e}' )
#
#            return rpt
#
#  return TestReport( num_test_cases = test_idx, failed = False )
#
##-------------------------------------------------------------------------
## global variable for hypothesis
##-------------------------------------------------------------------------
## Hacky
#
#test_idx = 1
#failed   = False
#rpt      = TestReport()
#
##-------------------------------------------------------------------------
## run_hypothesis_test
##-------------------------------------------------------------------------
#
#def run_hypothesis_test( opts ):
#
#  min_frac_nbits = opts.min_frac_nbits
#  max_frac_nbits = opts.max_frac_nbits
#  min_int_nbits  = opts.min_int_nbits
#  max_int_nbits  = opts.max_int_nbits
#  min_exp        = clog2( opts.min_N )
#  max_exp        = clog2( opts.max_N )
#
#  def _do_test( Type, N, x, trace=False, verbose=False ):
#    global failed
#
#    dut = FFTUnit( N, Type )
#    dut.elaborate()
#    dut.apply( SimulationPass )
#    dut.sim_reset()
#
#    dut_in = mk_fft_in( Type, x )
#    set_fft_in( dut, dut_in )
#    dut.tick()
#
#    if trace:
#      print( dut.line_trace() )
#
#    res = get_fft_out( dut )
#
#    ref = fft( x )
#
#    for a, b in zip( res, ref ):
#      if not almost_equal( a, b ):
#        err_msg = f'''\
#   - Test failed!
#   - x   = {x}
#   - ref = {ref}
#   - {a} != {b}
#'''
#        failed = True
#
#        if verbose:
#          print( 'Failed!' )
#          print( err_msg )
#
#        raise TestFailed( err_msg )
#
#  # Generate a hypothesis test
#
#  @hypothesis.settings( deadline = None, max_examples = opts.max_examples )
#  @hypothesis.given(
#    exp        = st.integers( min_exp, max_exp ),
#    frac_nbits = st.integers( min_frac_nbits, max_frac_nbits ),
#    int_nbits  = st.integers( min_int_nbits,  max_int_nbits  ),
#    seq        = st.data()
#  )
#  def _run( exp, frac_nbits, int_nbits, seq ):
#    global test_idx
#    global failed
#    global rpt
#
#    nbits      = frac_nbits + int_nbits
#    N          = 2 ** exp
#    complex_t  = mk_complex_fixed( nbits, frac_nbits )
#    min_value  = opts.min_value
#    max_value  = opts.max_value
#
#    x = seq.draw( sequence_strat( complex_t, N, min_value, max_value ) )
#    x = [ c.to_complex() for c in x ]
#
#    if opts.verbose:
#      print()
#      print( '-'*74 )
#
#      if not failed:
#        print( f' test case #{test_idx}' )
#      else:
#        print( ' shrinking...' )
#
#      print( '-'*74 )
#      print( f' - frac_nbits = {frac_nbits}' )
#      print( f' - int_nbits  = {int_nbits}' )
#      print( f' - N          = {N}' )
#      print( f' - x          = {x}' )
#
#    _do_test( complex_t, N, x, opts.trace )
#
#    # Exploring phase
#
#    if not failed:
#      test_idx += 1
#
#    # Shrinking phase - record data
#
#    else:
#      rpt = TestReport(
#        num_test_cases = test_idx,
#        error_msg      = f'hypothesis error',
#        seq            = x,
#        N              = N,
#        frac_nbits     = frac_nbits,
#        int_nbits      = int_nbits,
#      )
#
#  try:
#    _run()
#    return TestReport( num_test_cases = test_idx, failed = False )
#
#  except TestFailed as e:
#    rpt.error_msg = f'{e}'
#    return rpt
