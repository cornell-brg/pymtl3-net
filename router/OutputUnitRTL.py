#=========================================================================
# OutputUnitRTL.py
#=========================================================================
# An Output unit of the router. Just one normal queue, no credit.
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Feb 19, 2019

from pymtl import *
from pclib.ifcs import InValRdyIfc, OutValRdyIfc
from pclib.rtl  import NormalQueue1RTL

class OutputUnitRTL( RTLComponent ):
  # TODO: use multi-entry queue!
  def construct( s, num_entries, pkt_type ):
    
    # Interface
    s.in_ =  InValRdyIfc( pkt_type )
    s.out = OutValRdyIfc( pkt_type )

    if num_entries > 0:

      # Component
      # s.queue = NormalQueue( num_entries, pkt_type ) 
      s.queue = NormalQueue1RTL( pkt_type ) 

      # Connections
      s.connect( s.in_, s.queue.enq )
      s.connect( s.out, s.queue.deq )
    
    # No ouput queue
    else:
      s.connect( s.in_, s.out ) 

  def line_trace( s ):
    return "{} || {}".format( s.in_, s.out )
