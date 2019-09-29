"""
==========================================================================
utils.py
==========================================================================
Utility functions for pyocn script.

Author: Yanghui Ou
  Date: Sep 24, 2019

"""
from pymtl3 import *
from pymtl3.stdlib.cl.queues import BypassQueueCL

class CLNetWrapper( Component ):

  def construct( s, PktType, net, nports ):

    # Interface

    s.recv = [ NonBlockingCalleeIfc( PktType ) for _ in range( nports ) ]
    s.give = [ NonBlockingCalleeIfc( PktType ) for _ in range( nports ) ]

    # Component

    s.net   = net
    s.out_q = [ BypassQueueCL( num_entries=1 ) for _ in range( nports ) ]

    for i in range( nports ):
      connect( s.recv[i],      s.net.recv[i]  )
      connect( s.net.send[i],  s.out_q[i].enq )
      connect( s.out_q[i].deq, s.give[i]      )

  def line_trace( s ):
    return s.net.line_trace()