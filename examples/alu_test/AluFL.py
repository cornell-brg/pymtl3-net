"""
==========================================================================
AluFL.py
==========================================================================
A functional level queue. It can be used as the reference model for the
Verilog queue.

Author : Cheng Tan
  Date : July 18, 2019
"""
from __future__ import absolute_import, division, print_function

from collections import deque
from pymtl3 import *

class AluFL( Component ):

  def construct( s, RespType ):
    s.q = deque( maxlen=1 )
    s.RespType = RespType
#    s.nbits = nbits

  @non_blocking( lambda s: len(s.q) < s.q.maxlen )
  def enq( s, msg ):
    s.q.appendleft( msg )

  @non_blocking( lambda s: len(s.q) > 0 )
  def deq( s ):
    req    = s.q.pop()
    in1    = req.in1
    in2    = req.in2
    op     = req.op
    result = 0
    branch = 0
    if op == 0:
      result = in1 +  in2
    elif op == 1:
      result = in1 -  in2
    elif op == 2:
      result = in1 << in2
      branch = ( in1 == in2 )
    elif op == 3:
      result = in1 >> in2
      branch = ~ ( in1 == in2 )
    elif op == 4:
      result = in1 &  in2
      branch = ( in1 < in2 )
    elif op == 5:
      result = in1 |  in2
      branch = ( in1 < in2 ) | ( in1 == in2 )
    elif op == 6:
      result = in1 ^  in2
    elif op == 7:
      result = ~ in1
      branch = b1(1)

    result = s.RespType( result, branch )
    return result

  def line_trace( s ):
    return "{}->{}".format( s.enq, s.deq )
