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

  def construct( s, import_params ):

    # Metadata for import
    s.sverilog_params = import_params
    s.sverilog_import = True
    s.sverilog_import_path = "../Queue.sv"

    # Local parameter
    CountType = mk_bits( clog2( import_params["p_num_entries"]+1 ) )
    EntryType = mk_bits( import_params["p_data_width"] )

    # Interface
    s.count   =  OutPort( CountType  )

    s.deq_en  =  InPort( Bits1  )
    s.deq_rdy = OutPort( Bits1  )
    s.deq_msg = OutPort( EntryType )

    s.enq_en  =  InPort( Bits1  )
    s.enq_rdy = OutPort( Bits1  )
    s.enq_msg =  InPort( EntryType )

#-------------------------------------------------------------------------
# Wrapper
#-------------------------------------------------------------------------
# A wrapper that has method based interface around the verilog module.

class QueueVRTL( Component ):

  def construct( s, EntryType=Bits32, num_entries=2 ):
    s.enq   = EnqIfcRTL( EntryType )
    s.deq   = DeqIfcRTL( EntryType )
    s.count = OutPort  ( mk_bits( clog2( num_entries+1 ) ) )

    s.q = Queue({
      "p_data_width"  : EntryType.nbits,
      "p_num_entries" : num_entries,
    })

    s.connect( s.enq.en,  s.q.enq_en  )
    s.connect( s.enq.rdy, s.q.enq_rdy )
    s.connect( s.enq.msg, s.q.enq_msg )
    s.connect( s.deq.en,  s.q.deq_en  )
    s.connect( s.deq.rdy, s.q.deq_rdy )
    s.connect( s.deq.msg, s.q.deq_msg )
    s.connect( s.count,   s.q.count   )

  def line_trace( s ):
    return "{}({}){}".format( s.enq, s.count, s.deq )
