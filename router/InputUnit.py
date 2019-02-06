from pymtl import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.rtl  import NormalQueue

class InputUnit( Model ):
  """
  Input unit of the router. Just one normal queue, no virtual channels.
  """
  def __init__( s, num_entries, msg_type ):
    
    # Interfacel
    s.in_ =  InValRdyBundle( msg_type )
    s.out = OutValRdyBundle( msg_type )

    # Component
    s.queue = NormalQueue( num_entries, msg_type ) 
    
    # Connections
    s.connect( s.in_, s.queue.enq )
    s.connect( s.out, s.queue.deq )

  def line_trace( s ):
    return "{} || {}".format( s.in_, s.out )
