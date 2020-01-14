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