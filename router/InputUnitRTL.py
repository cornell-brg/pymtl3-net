#=========================================================================
# InputUnitRTL.py
#=========================================================================
# An input unit for the router that supports single-phit packet.
# Note that the interface is send/recv-based.
#
# Author : Yanghui Ou, Cheng Tan
#   Date : Feb 23, 2019

from pymtl import *
from pclib.ifcs import InValRdyIfc, OutValRdyIfc 
from pclib.rtl  import NormalQueueRTL

from pclib.ifcs.EnRdyIfc  import InEnRdyIfc, OutEnRdyIfc

class InputUnitRTL( RTLComponent ):
  def construct( s, num_entries, pkt_type ):

    # Interface
#    s.in_      =  InValRdyIfc( pkt_type )
#    s.out      = OutValRdyIfc( pkt_type )
    s.recv =  InEnRdyIfc( pkt_type )
    s.send = OutEnRdyIfc( pkt_type )

    # Component
    s.queue = NormalQueueRTL( num_entries, pkt_type )

    # Connections
#    s.connect( s.in_, s.queue.enq )
#    s.connect( s.out, s.queue.deq )
    s.connect( s.recv.rdy, s.queue.enq.rdy )
    s.connect( s.recv.en,  s.queue.enq.val )
    s.connect( s.recv.msg, s.queue.enq.msg )

    @s.update
    def store():
      s.send.msg  = s.queue.deq.msg
      s.send.en   = s.send.rdy and s.queue.deq.val
      s.queue.deq.rdy = s.send.rdy
  
  # TODO: implement line trace.
  def line_trace( s ):
    return "{} || {}".format( s.recv.msg, s.send.msg )
