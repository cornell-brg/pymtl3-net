#=========================================================================
# InputUnitCL.py
#=========================================================================
# Cycle level implementeation of the CL model.
#
# Author : Yanghui Ou
#   Date : May 16, 2019

from pymtl3                 import *
from pymtl3.stdlib.cl.queues       import NormalQueueCL

class InputUnitCL( Component ):

  def construct( s, PacketType, QueueType = NormalQueueCL ):

    # Interface

    s.recv = NonBlockingCalleeIfc()
    s.give = NonBlockingCalleeIfc()

    # Component

    s.queue = QueueType( size=2 )
    
    # Connections

    s.connect( s.recv,          s.queue.enq )
    s.connect( s.queue.deq,     s.give      )

  def line_trace( s ):
    return s.queue.line_trace()
