"""
==========================================================================
NormalQueueVRTL.py
==========================================================================
Imported NormalQueue from SystemVerilog.

Author : Yanghui Ou
  Date : July 10, 2019
"""

from __future__ import absolute_import, division, print_function

from pymtl3 import *
from pymtl3.dsl import Placeholder
from pymtl3.passes.sverilog import ImportPass
from pymtl3.stdlib.ifcs import DeqIfcRTL, EnqIfcRTL

#-------------------------------------------------------------------------
# Placeholder
#-------------------------------------------------------------------------
# A placeholder for the imported verilog module.

class Queue( Placeholder, Component ):

  def construct( s ):
    s.count   =  OutPort( Bits3  )

    s.deq_en  =  InPort( Bits1  )
    s.deq_rdy = OutPort( Bits1  )
    s.deq_msg = OutPort( Bits32 )

    s.enq_en  =  InPort( Bits1  )
    s.enq_rdy = OutPort( Bits1  )
    s.enq_msg =  InPort( Bits32 )

#-------------------------------------------------------------------------
# Wrapper
#-------------------------------------------------------------------------
# A wrapper that has method based interface around the verilog module.

class QueueVRTL( Component ):

  def construct( s ):
    s.enq   = EnqIfcRTL( Bits32 )
    s.deq   = DeqIfcRTL( Bits32 )
    s.count = OutPort  ( Bits3  )

    s.q = Queue()

    s.connect( s.enq.en,  s.q.enq_en  )
    s.connect( s.enq.rdy, s.q.enq_rdy )
    s.connect( s.enq.msg, s.q.enq_msg )
    s.connect( s.deq.en,  s.q.deq_en  )
    s.connect( s.deq.rdy, s.q.deq_rdy )
    s.connect( s.deq.msg, s.q.deq_msg )
    s.connect( s.count,   s.q.count   )

    # Metadata for import
    s.q.sverilog_import = True
    s.q.sverilog_import_path = "../Queue.sv"

  def line_trace( s ):
    return "{}({}){}".format( s.enq, s.count, s.deq )
