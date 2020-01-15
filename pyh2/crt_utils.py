'''
==========================================================================
crt_utils.py
==========================================================================
Utilities for complete random test.

Author : Yanghui Ou
  Date : Jan 14, 2020
'''
import random
from ocn_pclib.ifcs.packets import mk_ring_pkt

from common_utils import TestReport, run_test_case

#--------------------------------------------------------------------------
# rand_pkt
#--------------------------------------------------------------------------

def rand_pkt( PktType, nterminals ):
  src     = random.randint(0, nterminals-1)
  dst     = random.randint(0, nterminals-1)
  payload = random.randint(0, 255) # Assumes payload is at least 8 bits
  return PktType( src=src, dst=dst, payload=payload, vc_id=0 )

#--------------------------------------------------------------------------
# run_crt
#--------------------------------------------------------------------------

def run_crt( opts ):
  max_nterminals = opts.max_nterminals
  max_ntrans      = opts.max_ntrans

  for i in range( opts.max_examples ):
    nterminals = random.randint(2, max_nterminals)
    ntrans     = random.randint(1, max_ntrans)
    PktType    = mk_ring_pkt( nterminals )
    test_seq   = [ rand_pkt( PktType, nterminals ) for _ in range(ntrans) ]

    run_test_case( nterminals, test_seq, max_cycles=ntrans*50, translate=opts.translate, trace=False )

    try:
      if opts.verbose:
        print()
        print( '-'*74 )
        print( f'crt #{i+1}' )
        print( '-'*74 )
        print( f'  + nterminals: {nterminals}' )
        print( f'  + ntransactions: {ntrans}' )
        print( f'  + test sequence:' )
        print( '    ' + '\n    '.join([ str(p) for p in test_seq]) )

      run_test_case( nterminals, test_seq, max_cycles=ntrans*50, translate=opts.translate, trace=False )

    except Exception as e:
      rpt = TestReport(
        ntests     = i+1,
        ntrans     = ntrans,
        nterminals = nterminals,
        failed     = True,
      )
      if opts.verbose:
        print( f'{e}' )

  return TestReport( nterminals=opts.max_examples, failed=False )
