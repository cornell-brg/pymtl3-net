'''
==========================================================================
idt_utils.py
==========================================================================
Utilities for iterative deepened test.

Author : Yanghui Ou
  Date : Jan 14, 2020
'''
import random
from ocn_pclib.ifcs.packets import mk_ring_pkt
from common_utils import TestReport, run_test_case
from crt_utils import rand_pkt

#-------------------------------------------------------------------------
# _calc_step
#-------------------------------------------------------------------------

def _calc_step( min_val, max_val, r=5 ):
  assert max_val >= min_val
  step = ( max_val - min_val ) // r
  if step == 0:
    return 1
  else:
    return step

#-------------------------------------------------------------------------
# idt_range
#-------------------------------------------------------------------------

def idt_range( cur_val, max_val, step ):
  return range( cur_val, min( max_val, cur_val+step )+1 )

#-------------------------------------------------------------------------
# run_idt
#-------------------------------------------------------------------------
# TODO: time out after certain number of test cases?

def run_idt( opts ):
  min_nterminals = 2
  max_nterminals = opts.max_nterminals
  min_ntrans     = 1
  max_ntrans     = opts.max_ntrans

  test_idx  = 1
  cur_nterm = min_nterminals
  cur_ntran = min_ntrans

  step_nterm = _calc_step( min_nterminals, max_nterminals )
  step_ntran = _calc_step( min_ntrans,     max_ntrans     )

  while cur_nterm <= max_nterminals or cur_ntran <= max_ntrans:
    for nterminals in idt_range( cur_nterm, max_nterminals, step_nterm ):
      for ntrans in idt_range( cur_ntran, max_ntrans, step_ntran ):
        for _ in range( opts.tests_per_step ):

          PktType  = mk_ring_pkt( nterminals )
          test_seq = [ rand_pkt( PktType, nterminals ) for _ in range(ntrans) ]

          try:
            if opts.verbose:
              print()
              print( '-'*74 )
              print( f'idt #{test_idx}' )
              print( '-'*74 )
              print( f'  + nterminals: {nterminals}' )
              print( f'  + ntransactions: {ntrans}' )
              print( f'  + test sequence:' )
              print( '    ' + '\n    '.join([ str(p) for p in test_seq]) )

            run_test_case( nterminals, test_seq, max_cycles=ntrans*50, translate=opts.translate, trace=False )
            test_idx += 1

          except Exception as e:
            rpt = TestReport(
              ntests     = test_idx,
              ntrans     = ntrans,
              nterminals = nterminals,
              complexity = avg_complexity( test_seq ),
              failed     = True,
            )
            if opts.verbose:
              print( f'{e}' )

    cur_nterm += step_nterm
    cur_ntran += step_ntran

  return TestReport( ntests=test_idx, failed=False )
