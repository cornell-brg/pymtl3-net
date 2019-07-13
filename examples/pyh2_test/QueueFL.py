"""
==========================================================================
QueueFL.py
==========================================================================
A functional level queue.

Author : Yanghui Ou
  Date : July 12, 2019
"""
from __future__ import absolute_import, division, print_function

from collections import deque
from pymtl3 import *

class QueueFL( Component ):

  def construct( s, num_entries=2 ):
    s.q = deque( maxlen=num_entries )

  @non_blocking( lambda s: len(s.q) < s.q.maxlen )
  def enq( s, msg ):
    s.q.appendleft( msg )

  @non_blocking( lambda s: len(s.q) > 0 )
  def deq( s ):
    return s.q.pop()

  def line_trace( s ):
    return "{}(){}".format( s.enq, s.deq )