#=========================================================================
# OutputUnit.py
#=========================================================================
# An Output unit of the router. Just one normal queue, no credit.
#
# Author : Yanghui Ou, Cheng Tan
#   Date : Feb 18, 2019

from pymtl import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.rtl  import NormalQueue

class OutputUnit( Model ):
  def __init__( s, num_entries, msg_type ):
    
    # Interfacel
    s.in_ =  InValRdyBundle( msg_type )
    s.out = OutValRdyBundle( msg_type )

    # Component
    if num_entries > 0:
      s.queue = NormalQueue( num_entries, msg_type ) 
      s.connect( s.in_, s.queue.enq )
      s.connect( s.out, s.queue.deq )
    
    # No ouput queue
    else:
      s.connect( s.in_, s.out ) 

  def line_trace( s ):
    return "{} || {}".format( s.in_, s.out )
