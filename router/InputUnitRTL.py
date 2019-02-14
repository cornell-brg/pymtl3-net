#=========================================================================
# InputUnitRTL.py
#=========================================================================
# An input unit for the router that supports single-phit packet.
#
# Author : Yanghui Ou, Cheng Tan
#   Date : Feb 14, 2019

from pymtl import *
from pclib.ifcs import InValRdyIfc, OutValRdyIfc 
from pclib.rtl  import NormalQueue1RTL

class InputUnitRTL( RTLComponent ):
  # TODO: use multi-entry queue!
  def construct( s, num_entries, pkt_type ):

    # Interface
    s.in_ =  InValRdyIfc( pkt_type )
    s.out = OutValRdyIfc( pkt_type )

    # Component
    s.queue = NormalQueue1RTL( pkt_type )

    # Connections
    s.connect( s.in_, s.queue.enq )
    s.connect( s.out, s.queue.deq )
  
  # TODO: implement line trace.
  def line_trace( s ):
    return ""
