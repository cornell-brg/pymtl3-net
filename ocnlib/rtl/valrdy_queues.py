"""
==========================================================================
Library of RTL queues
==========================================================================
This is a modified version of pymtl3 rtl queues. The only difference is
that the rdy signal no longer depends on reset.

Author : Yanghui Ou
  Date : Mar 31, 2020
"""


from pymtl3 import *
from pymtl3.stdlib.ifcs import InValRdyIfc, OutValRdyIfc
# from pymtl3.stdlib.queues import DeqIfcRTL, EnqIfcRTL
from pymtl3.stdlib.basic_rtl.arithmetics import Mux
from pymtl3.stdlib.basic_rtl import RegisterFile

#-------------------------------------------------------------------------
# Dpath and Ctrl for NormalQueueRTL
#-------------------------------------------------------------------------

class NormalQueueDpathRTL( Component ):

  def construct( s, EntryType, num_entries=2 ):

    # Interface

    s.enq_msg =  InPort( EntryType )
    s.deq_msg = OutPort( EntryType )

    s.wen   = InPort( Bits1 )
    s.waddr = InPort( mk_bits( clog2( num_entries ) ) )
    s.raddr = InPort( mk_bits( clog2( num_entries ) ) )

    # Component

    s.queue = m = RegisterFile( EntryType, num_entries )
    m.raddr[0] //= s.raddr
    m.rdata[0] //= s.deq_msg
    m.wen[0]   //= s.wen
    m.waddr[0] //= s.waddr
    m.wdata[0] //= s.enq_msg

class NormalQueueCtrlRTL( Component ):

  def construct( s, num_entries=2 ):

    # Constants

    addr_nbits    = clog2    ( num_entries   )
    count_nbits   = clog2    ( num_entries+1 )
    PtrType       = mk_bits  ( addr_nbits    )
    CountType     = mk_bits  ( count_nbits   )
    s.last_idx    = PtrType  ( num_entries-1 )
    s.num_entries = CountType( num_entries   )

    # Interface

    s.enq_val = InPort ( Bits1     )
    s.enq_rdy = OutPort( Bits1     )
    s.deq_val = OutPort( Bits1     )
    s.deq_rdy = InPort ( Bits1     )
    s.count   = OutPort( CountType )

    s.wen     = OutPort( Bits1   )
    s.waddr   = OutPort( PtrType )
    s.raddr   = OutPort( PtrType )

    # Registers

    s.head = Wire( PtrType )
    s.tail = Wire( PtrType )

    # Wires

    s.enq_xfer  = Wire( Bits1   )
    s.deq_xfer  = Wire( Bits1   )

    # Connections

    connect( s.wen,   s.enq_xfer )
    connect( s.waddr, s.tail     )
    connect( s.raddr, s.head     )

    s.enq_rdy //= lambda: s.count < s.num_entries
    s.deq_val //= lambda: s.count > 0

    s.enq_xfer //= lambda: s.enq_val & s.enq_rdy
    s.deq_xfer //= lambda: s.deq_rdy & s.deq_val

    @update_ff
    def up_reg():

      if s.reset:
        s.head  <<= 0
        s.tail  <<= 0
        s.count <<= 0

      else:
        if s.deq_xfer:
          s.head <<= s.head + 1 if s.head < s.last_idx else 0

        if s.enq_xfer:
          s.tail <<= s.tail + 1 if s.tail < s.last_idx else 0

        if s.enq_xfer & ~s.deq_xfer:
          s.count <<= s.count + 1
        if ~s.enq_xfer & s.deq_xfer:
          s.count <<= s.count - 1

#-------------------------------------------------------------------------
# NormalQueueRTL
#-------------------------------------------------------------------------

class NormalQueueRTL( Component ):

  def construct( s, EntryType, num_entries=2 ):

    # Interface

    s.enq   = InValRdyIfc ( EntryType )
    s.deq   = OutValRdyIfc( EntryType )
    s.count = OutPort( mk_bits( clog2( num_entries+1 ) ) )

    # Components

    assert num_entries > 0
    if num_entries == 1:
      s.q = NormalQueue1EntryRTL( EntryType )
      connect( s.enq,   s.q.enq )
      connect( s.deq,   s.q.deq )
      connect( s.count, s.q.count )

    else:
      s.ctrl  = NormalQueueCtrlRTL ( num_entries )
      s.dpath = NormalQueueDpathRTL( EntryType, num_entries )

      # Connect ctrl to data path

      connect( s.ctrl.wen,     s.dpath.wen     )
      connect( s.ctrl.waddr,   s.dpath.waddr   )
      connect( s.ctrl.raddr,   s.dpath.raddr   )

      # Connect to interface

      connect( s.enq.val, s.ctrl.enq_val  )
      connect( s.enq.rdy, s.ctrl.enq_rdy  )
      connect( s.deq.val, s.ctrl.deq_val  )
      connect( s.deq.rdy, s.ctrl.deq_rdy  )
      connect( s.count,   s.ctrl.count    )
      connect( s.enq.msg, s.dpath.enq_msg )
      connect( s.deq.msg, s.dpath.deq_msg )

  # Line trace

  def line_trace( s ):
    return f"{s.enq}({s.count}){s.deq}"

#-------------------------------------------------------------------------
# Ctrl for PipeQueue
#-------------------------------------------------------------------------

# class PipeQueueCtrlRTL( Component ):

#   def construct( s, num_entries=2 ):

#     # Constants

#     addr_nbits    = clog2    ( num_entries   )
#     count_nbits   = clog2    ( num_entries+1 )
#     PtrType       = mk_bits  ( addr_nbits    )
#     CountType     = mk_bits  ( count_nbits   )
#     s.last_idx    = PtrType  ( num_entries-1 )
#     s.num_entries = CountType( num_entries   )

#     # Interface

#     s.enq_en  = InPort ( Bits1     )
#     s.enq_rdy = OutPort( Bits1     )
#     s.deq_en  = InPort ( Bits1     )
#     s.deq_rdy = OutPort( Bits1     )
#     s.count   = OutPort( CountType )

#     s.wen     = OutPort( Bits1   )
#     s.waddr   = OutPort( PtrType )
#     s.raddr   = OutPort( PtrType )

#     # Registers

#     s.head = Wire( PtrType )
#     s.tail = Wire( PtrType )

#     # Wires

#     s.enq_xfer  = Wire( Bits1   )
#     s.deq_xfer  = Wire( Bits1   )

#     # Connections

#     connect( s.wen,   s.enq_xfer )
#     connect( s.waddr, s.tail     )
#     connect( s.raddr, s.head     )

#     s.deq_rdy //= lambda: s.count > 0
#     s.enq_rdy //= lambda: ( s.count < s.num_entries ) | s.deq_en

#     s.enq_xfer //= lambda: s.enq_en & s.enq_rdy
#     s.deq_xfer //= lambda: s.deq_en & s.deq_rdy

#     @s.update_ff
#     def up_reg():

#       if s.reset:
#         s.head  <<= 0
#         s.tail  <<= 0
#         s.count <<= 0

#       else:
#         if s.deq_xfer:
#           s.head <<= s.head + 1 if s.head < s.last_idx else 0

#         if s.enq_xfer:
#           s.tail <<= s.tail + 1 if s.tail < s.last_idx else 0

#         if s.enq_xfer & ~s.deq_xfer:
#           s.count <<= s.count + 1
#         if ~s.enq_xfer & s.deq_xfer:
#           s.count <<= s.count - 1

#-------------------------------------------------------------------------
# PipeQueueRTL
#-------------------------------------------------------------------------

# class PipeQueueRTL( Component ):

#   def construct( s, EntryType, num_entries=2 ):

#     # Interface

#     s.enq   = EnqIfcRTL( EntryType )
#     s.deq   = DeqIfcRTL( EntryType )
#     s.count = OutPort( mk_bits( clog2( num_entries+1 ) ) )

#     # Components

#     assert num_entries > 0
#     if num_entries == 1:
#       s.q = PipeQueue1EntryRTL( EntryType )
#       connect( s.enq,   s.q.enq )
#       connect( s.deq,   s.q.deq )
#       connect( s.count, s.q.count )

#     else:
#       s.ctrl  = PipeQueueCtrlRTL ( num_entries )
#       s.dpath = NormalQueueDpathRTL( EntryType, num_entries )

#       # Connect ctrl to data path

#       connect( s.ctrl.wen,     s.dpath.wen     )
#       connect( s.ctrl.waddr,   s.dpath.waddr   )
#       connect( s.ctrl.raddr,   s.dpath.raddr   )

#       # Connect to interface

#       connect( s.enq.en,  s.ctrl.enq_en   )
#       connect( s.enq.rdy, s.ctrl.enq_rdy  )
#       connect( s.deq.en,  s.ctrl.deq_en   )
#       connect( s.deq.rdy, s.ctrl.deq_rdy  )
#       connect( s.count,   s.ctrl.count    )
#       connect( s.enq.msg, s.dpath.enq_msg )
#       connect( s.deq.ret, s.dpath.deq_ret )

#   # Line trace

#   def line_trace( s ):
#     return "{}({}){}".format( s.enq, s.count, s.deq )

#-------------------------------------------------------------------------
# Ctrl and Dpath for BypassQueue
#-------------------------------------------------------------------------

# class BypassQueueDpathRTL( Component ):

#   def construct( s, EntryType, num_entries=2 ):

#     # Interface

#     s.enq_msg =  InPort( EntryType )
#     s.deq_ret = OutPort( EntryType )

#     s.wen     = InPort( Bits1 )
#     s.waddr   = InPort( mk_bits( clog2( num_entries ) ) )
#     s.raddr   = InPort( mk_bits( clog2( num_entries ) ) )
#     s.mux_sel = InPort( Bits1 )

#     # Component

#     s.queue = m =RegisterFile( EntryType, num_entries )
#     m.raddr[0] //= s.raddr
#     m.wen[0]   //= s.wen
#     m.waddr[0] //= s.waddr
#     m.wdata[0] //= s.enq_msg

#     s.mux = Mux( EntryType, 2 )
#     s.mux.sel    //= s.mux_sel
#     s.mux.in_[0] //= s.queue.rdata[0]
#     s.mux.in_[1] //= s.enq_msg
#     s.mux.out    //= s.deq_ret

# class BypassQueueCtrlRTL( Component ):

#   def construct( s, num_entries=2 ):

#     # Constants

#     addr_nbits    = clog2    ( num_entries   )
#     count_nbits   = clog2    ( num_entries+1 )
#     PtrType       = mk_bits  ( addr_nbits    )
#     CountType     = mk_bits  ( count_nbits   )
#     s.last_idx    = PtrType  ( num_entries-1 )
#     s.num_entries = CountType( num_entries   )

#     # Interface

#     s.enq_en  = InPort ( Bits1     )
#     s.enq_rdy = OutPort( Bits1     )
#     s.deq_en  = InPort ( Bits1     )
#     s.deq_rdy = OutPort( Bits1     )
#     s.count   = OutPort( CountType )

#     s.wen     = OutPort( Bits1   )
#     s.waddr   = OutPort( PtrType )
#     s.raddr   = OutPort( PtrType )
#     s.mux_sel = OutPort( Bits1   )

#     # Registers

#     s.head = Wire( PtrType )
#     s.tail = Wire( PtrType )

#     # Wires

#     s.enq_xfer  = Wire( Bits1   )
#     s.deq_xfer  = Wire( Bits1   )

#     # Connections

#     connect( s.wen,   s.enq_xfer )
#     connect( s.waddr, s.tail     )
#     connect( s.raddr, s.head     )

#     s.enq_rdy //= lambda: s.count < s.num_entries
#     s.deq_rdy //= lambda: ( s.count > 0 ) | s.enq_en

#     s.mux_sel //= lambda: s.count == 0

#     s.enq_xfer //= lambda: s.enq_en & s.enq_rdy
#     s.deq_xfer //= lambda: s.deq_en & s.deq_rdy

#     @s.update_ff
#     def up_reg():

#       if s.reset:
#         s.head  <<= PtrType(0)
#         s.tail  <<= PtrType(0)
#         s.count <<= CountType(0)

#       else:
#         if s.deq_xfer:
#           s.head <<= s.head + 1 if s.head < s.last_idx else 0

#         if s.enq_xfer:
#           s.tail <<= s.tail + 1 if s.tail < s.last_idx else 0

#         if s.enq_xfer & ~s.deq_xfer:
#           s.count <<= s.count + 1
#         if ~s.enq_xfer & s.deq_xfer:
#           s.count <<= s.count - 1

#-------------------------------------------------------------------------
# BypassQueueRTL
#-------------------------------------------------------------------------

# class BypassQueueRTL( Component ):

#   def construct( s, EntryType, num_entries=2 ):

#     # Interface

#     s.enq   = EnqIfcRTL( EntryType )
#     s.deq   = DeqIfcRTL( EntryType )
#     s.count = OutPort( mk_bits( clog2( num_entries+1 ) ) )

#     # Components

#     assert num_entries > 0
#     if num_entries == 1:
#       s.q = BypassQueue1EntryRTL( EntryType )
#       connect( s.enq,   s.q.enq )
#       connect( s.deq,   s.q.deq )
#       connect( s.count, s.q.count )

#     else:
#       s.ctrl  = BypassQueueCtrlRTL ( num_entries )
#       s.dpath = BypassQueueDpathRTL( EntryType, num_entries )

#       # Connect ctrl to data path

#       connect( s.ctrl.wen,     s.dpath.wen     )
#       connect( s.ctrl.waddr,   s.dpath.waddr   )
#       connect( s.ctrl.raddr,   s.dpath.raddr   )
#       connect( s.ctrl.mux_sel, s.dpath.mux_sel )

#       # Connect to interface

#       connect( s.enq.en,  s.ctrl.enq_en   )
#       connect( s.enq.rdy, s.ctrl.enq_rdy  )
#       connect( s.deq.en,  s.ctrl.deq_en   )
#       connect( s.deq.rdy, s.ctrl.deq_rdy  )
#       connect( s.count,   s.ctrl.count    )
#       connect( s.enq.msg, s.dpath.enq_msg )
#       connect( s.deq.ret, s.dpath.deq_ret )

#   # Line trace

#   def line_trace( s ):
#     return f"{s.enq}({s.count}){s.deq}"

#-------------------------------------------------------------------------
# NormalQueue1EntryRTL
#-------------------------------------------------------------------------

class NormalQueue1EntryRTL( Component ):

  def construct( s, EntryType ):

    # Interface

    s.enq   = InValRdyIfc ( EntryType )
    s.deq   = OutValRdyIfc( EntryType )
    s.count = OutPort  ( Bits1     )

    # Components

    s.entry = Wire( EntryType )
    s.full  = Wire( Bits1 )

    s.enq_xfer = Wire(Bits1)
    s.deq_xfer = Wire(Bits1)

    # Logic

    s.count //= s.full

    s.deq.msg //= s.entry

    s.enq_xfer //= lambda: s.enq.val & s.enq.rdy
    s.deq_xfer //= lambda: s.deq.val & s.deq.rdy

    s.enq.rdy //= lambda: ~s.full
    s.deq.val //= lambda: s.full

    @update_ff
    def ff_normal1():
      s.full <<= ~s.reset & ( ~s.deq_xfer & (s.enq_xfer | s.full) )
      if s.enq_xfer:
        s.entry <<= s.enq.msg

  def line_trace( s ):
    return f"{s.enq}({s.full}){s.deq}"

#-------------------------------------------------------------------------
# PipeQueue1EntryRTL
#-------------------------------------------------------------------------

# class PipeQueue1EntryRTL( Component ):

#   def construct( s, EntryType ):

#     # Interface

#     s.enq   = EnqIfcRTL( EntryType )
#     s.deq   = DeqIfcRTL( EntryType )
#     s.count = OutPort  ( Bits1     )

#     # Components

#     s.entry = Wire( EntryType )
#     s.full  = Wire( Bits1 )

#     # Logic

#     s.count //= s.full

#     s.deq.ret //= s.entry

#     s.enq.rdy //= lambda: ~s.full | s.deq.en
#     s.deq.rdy //= lambda: s.full

#     @s.update_ff
#     def ff_pipe1():
#       s.full <<= ~s.reset & ( s.enq.en | s.full & ~s.deq.en )

#       if s.enq.en:
#         s.entry <<= s.enq.msg

#   def line_trace( s ):
#     return f"{s.enq}({s.full}){s.deq}"

#-------------------------------------------------------------------------
# BypassQueue1EntryRTL
#-------------------------------------------------------------------------

# class BypassQueue1EntryRTL( Component ):

#   def construct( s, EntryType ):

#     # Interface

#     s.enq   = EnqIfcRTL( EntryType )
#     s.deq   = DeqIfcRTL( EntryType )
#     s.count = OutPort  ( Bits1     )

#     # Components

#     s.entry = Wire( EntryType )
#     s.full  = Wire( Bits1 )

#     s.bypass_mux = Mux( EntryType, 2 )
#     s.bypass_mux.in_[0] //= s.enq.msg
#     s.bypass_mux.in_[1] //= s.entry
#     s.bypass_mux.out    //= s.deq.ret
#     s.bypass_mux.sel    //= s.full

#     # Logic

#     s.count //= s.full

#     s.enq.rdy //= lambda: ~s.full
#     s.deq.rdy //= lambda: ( s.full | s.enq.en )

#     @s.update_ff
#     def ff_bypass1():
#       s.full <<= ~s.reset & ( ~s.deq.en & (s.enq.en | s.full) )

#       if s.enq.en & ~s.deq.en:
#         s.entry <<= s.enq.msg

#   def line_trace( s ):
#     return f"{s.enq}({s.full}){s.deq}"
