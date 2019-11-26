#!/usr/bin/env python
'''
==========================================================================
 run_test.py
==========================================================================
Driver script that runs tests with different methodologies.

Author : Yanghui Ou
  Date : Nov 22, 2019

'''
import argparse
import sys
import os
from pymtl3 import *

from utils import *

#-------------------------------------------------------------------------
# add_generic_args
#-------------------------------------------------------------------------
# Helper function that adds the generic arguments to the command line
# parser.

def add_generic_args( p ):
  p.add_argument( '-s', '--trace',   action='store_true', help='show line trace' )
  p.add_argument( '-v', '--verbose', action='store_true', help='verbose mode' )
  p.add_argument(       '--min-N', type=int, default=2,  metavar='', help='min value for number of inputs. Must be a power of 2' )
  p.add_argument(       '--max-N', type=int, default=16, metavar='', help='max value for number of inputs. Must be a power of 2' )
  p.add_argument(       '--min-frac-nbits', type=int, default=8,  metavar='', help='min number of fraction bits' )
  p.add_argument(       '--max-frac-nbits', type=int, default=16, metavar='', help='max number of fraction bits' )
  p.add_argument(       '--min-int-nbits',  type=int, default=16, metavar='', help='min number of integer bits' )
  p.add_argument(       '--max-int-nbits',  type=int, default=48, metavar='', help='max number of integer bits' )
  p.add_argument(       '--min-value',      type=float, default=-16.0, metavar='', help='min value for real and imag part' )
  p.add_argument(       '--max-value',      type=float, default=16.0,  metavar='', help='max value for real and imag part' )

#=========================================================================
# Multi-level command line parser
#=========================================================================

class Driver:

  def __init__( self ):
    parser = argparse.ArgumentParser(
      description = 'Driver script to run tests with different methodologies',
      usage = '''\
./run_test.py <method> [<flags>]

Available methods are:
  random      Pure random.
  iter        Iterative deepening.
  hypothesis  Property-based testing.
''')

    parser.add_argument( 'method', choices=['iter', 'random', 'hypothesis'], help='testing method to use' )
    self.parser = parser

    # Only parse the first arg

    args = parser.parse_args( sys.argv[1:2] )

    # Execute the corresponding function

    getattr( self, args.method )()

  #-----------------------------------------------------------------------
  # random
  #-----------------------------------------------------------------------

  def random( self ):
    p = argparse.ArgumentParser(
      description = 'Pure random test.',
      usage = '''\
./run_test.py random [<flags>]
''')

    p.add_argument( '--max-examples', type=int, default=100, metavar='', help='maximum number of test cases to run' )
    add_generic_args( p )

    # Parse the remaining command

    opts = p.parse_args( sys.argv[2:] )

    rpt = run_random_test( opts )

    print( '-'*74 )
    print( ' report' )
    print( '-'*74 )

    if rpt.failed:
      print( f' - bug found with {rpt.num_test_cases} test cases' )
      print( f' - failing test case:' )
      print( f'     + nrouters   = {rpt.nrouters}'          )
      print( f'     + ntrans     = {rpt.ntrans}' )

    else:
      print( f' - {rpt.num_test_cases} test cases passed.' )

  #-----------------------------------------------------------------------
  # iter
  #-----------------------------------------------------------------------

  def iter( self ):
    p = argparse.ArgumentParser(
      description = 'Iterative deepening based random test',
      usage = '''\
./run_test.py iter [<flags>]
''')

    p.add_argument( '--tests-per-step', type=int, default=10, metavar='', help='number of tests per step' )
    add_generic_args( p )

    # Parse the remaining command

    opts = p.parse_args( sys.argv[2:] )

    rpt = run_iter_test( opts )

    print( '-'*74 )
    print( ' report' )
    print( '-'*74 )

    if rpt.failed:
      print( f' - bug found with {rpt.num_test_cases} test cases' )
      print( f' - failing test case:' )
      print( f'     + nrouters   = {rpt.nrouters}'          )
      print( f'     + ntrans     = {rpt.ntrans}' )

    else:
      print( f' - {rpt.num_test_cases} test cases passed.' )

  #-----------------------------------------------------------------------
  # hypothesis
  #-----------------------------------------------------------------------

  def hypothesis( self ):
    p = argparse.ArgumentParser(
      description = 'Random property-based test',
      usage = '''\
./run_test.py hypothesis [<flags>]
''')
    p.add_argument( '--max-examples', type=int, default=100, metavar='', help='maximum number of test cases to run' )
    add_generic_args( p )

    # Parse the remaining command

    opts = p.parse_args( sys.argv[2:] )

    rpt = run_hypothesis_test( opts )

    print( '-'*74 )
    print( ' report' )
    print( '-'*74 )

    if rpt.failed:
      print( f' - bug found with {rpt.num_test_cases} test cases' )
      print( f' - failing test case:' )
      print( f'     + nrouters   = {rpt.nrouters}'          )
      print( f'     + ntrans     = {rpt.ntrans}' )

    else:
      print( f' - {rpt.num_test_cases} test cases passed.' )

#=========================================================================
# main
#=========================================================================

if __name__ == '__main__':
  Driver()
