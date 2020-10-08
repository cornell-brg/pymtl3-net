'''
==========================================================================
PitonSwitchUnitOpt.py
==========================================================================
Switch unit that supports multi-flit (single-phit flit) packet.

R.I.P. Kobe.

Author : Yanghui Ou
  Date : Oct 5, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.basic_rtl import Mux, Encoder
from pymtl3.stdlib.ifcs import InValRdyIfc, OutValRdyIfc
from ocnlib.rtl import Counter, GrantHoldArbiter
from ocnlib.rtl.valrdy_queues import NormalQueueValRdy

from .directions import *
from .PitonNoCHeader import PitonNoCHeader, PitonInternalFlit

class PitonSwitchUnitOpt( Component ):

  def construct( s, num_inports=5, speculative_input=NORTH ):

    # Local parameters
    assert PitonNoCHeader.nbits == 64
    s.num_inports = 5
    s.PhitType    = Bits64
    s.sel_width   = clog2( num_inports )
    s.SPEC_SRC    = speculative_input

    s.STATE_HEADER        = b2(0)
    s.STATE_BODY_NORMAL   = b2(1)
    s.STATE_BODY_STRAIGHT = b2(2)

    # Interface
    s.in_  = [ InValRdyIfc( PitonInternalFlit ) for _ in range( s.num_inports )  ]
    s.out  = OutValRdyIfc( s.PhitType )

    s.hold    = InPort( s.num_inports ) # indicates is_body

    # Components

    s.state      = Wire( Bits2 )
    s.state_next = Wire( Bits2 )

    s.any_hold        = Wire()
    s.any_val         = Wire()

    s.granted_val     = Wire()

    s.straight_go      = Wire()
    s.straight_val     = Wire()
    s.straight_msg     = Wire( s.PhitType )
    s.straight_is_tail = Wire()

    s.out_xfer        = Wire()
    s.enq_xfer        = Wire()

    # s.arbiter_reqs    = Wire( mk_bits( s.num_inports ) )

    s.arbiter = GrantHoldArbiter( nreqs=s.num_inports )
    s.arbiter.hold //= s.any_hold
    s.arbiter.en   //= lambda: ~s.any_hold & s.out.val & s.out.rdy # TODO

    s.mux = Mux( PitonInternalFlit, s.num_inports )
    # s.mux.out //= s.out.msg
    # s.mux_sel //= s.mux_sel_r

    s.encoder = Encoder( s.num_inports, s.sel_width )
    s.encoder.in_  //= s.arbiter.grants
    s.encoder.out  //= s.mux.sel

    s.queue = NormalQueueValRdy( PitonInternalFlit, num_entries=2 )
    s.queue.enq.val  //= s.granted_val
    s.queue.enq.msg  //= s.mux.out

    # Direct connections

    s.straight_val     //= s.in_[ s.SPEC_SRC ].val
    s.straight_msg     //= s.in_[ s.SPEC_SRC ].msg.flit
    s.straight_is_tail //= s.in_[ s.SPEC_SRC ].msg.is_tail

    s.out_xfer //= lambda: s.out.val & s.out.rdy
    s.enq_xfer //= lambda: s.queue.enq.val & s.queue.enq.rdy

    # State Transition Logic

    @update_ff
    def up_state_r():
      if s.reset:
        s.state <<= s.STATE_HEADER
      else:
        s.state <<= s.state_next

    @update
    def up_state_next():
      s.state_next @= s.state

      # If the header gets sent out and that the output is not allocated
      # in the last cycle

      if s.state == s.STATE_HEADER:
        if s.out.rdy & s.straight_val & ~s.straight_is_tail & ~s.queue.deq.val:
          s.state_next @= s.STATE_BODY_STRAIGHT

        # Contended case - use normal route
        elif s.out.rdy & s.queue.deq.val & ~s.queue.deq.msg.is_tail:
          s.state_next @= s.STATE_BODY_NORMAL

      elif s.state == s.STATE_BODY_STRAIGHT:
        if s.out_xfer & s.straight_is_tail:
          s.state_next @= s.STATE_HEADER

      else: # s.state == s.STATE_BODY_NORMAL
        if s.out_xfer & s.queue.deq.msg.is_tail:
          s.state_next @= s.STATE_HEADER

    # State Output Logic
    # - s.out.msg
    # - s.out.val
    # - s.queue.deq.rdy
    # - s.in_[i].rdy
    # - s.arbiter.reqs[i]

    @update
    def up_state_output():

      # Header state

      if s.state == s.STATE_HEADER:
        s.out.msg @= s.queue.deq.msg.flit if s.queue.deq.val else \
                     s.straight_msg
        s.out.val @= s.straight_val if ~s.queue.deq.val else \
                     s.queue.deq.val

        s.queue.deq.rdy @= s.out.rdy

        # Normal route
        if s.queue.deq.val:
          for i in range( s.num_inports ):
            s.in_[i].rdy @= s.queue.enq.rdy & ( s.mux.sel == i ) & \
                            ( s.arbiter.grants > 0 )
            s.arbiter.reqs[i] @= s.in_[i].val

        # Straight route
        else:
          for i in range( s.num_inports ):
            s.in_[i].rdy @= s.queue.enq.rdy & ( s.mux.sel == i ) & \
                            ( s.arbiter.grants > 0 )
            s.arbiter.reqs[i] @= s.in_[i].val

          s.arbiter.reqs[ s.SPEC_SRC ] @= 0
          s.in_[ s.SPEC_SRC ].rdy @= s.out.rdy

      # Body state for straight route

      elif s.state == s.STATE_BODY_STRAIGHT:
        s.out.msg @= s.straight_msg
        s.out.val @= s.straight_val

        s.queue.deq.rdy @= 0

        for i in range( s.num_inports ):
          s.in_[i].rdy @= s.queue.enq.rdy & ( s.mux.sel == i ) & \
                          ( s.arbiter.grants > 0 )
          s.arbiter.reqs[i] @= s.in_[i].val

        s.arbiter.reqs[ s.SPEC_SRC ] @= 0
        s.in_[ s.SPEC_SRC ].rdy @= s.out.rdy

      # Body state for normal route

      else: # s.state == s.STATE_BODY_NORMAL
        s.out.msg @= s.queue.deq.msg.flit
        s.out.val @= s.queue.deq.val

        s.queue.deq.rdy @= s.out.rdy

        for i in range( s.num_inports ):
          s.in_[i].rdy @= s.queue.enq.rdy & ( s.mux.sel == i ) & \
                          ( s.arbiter.grants > 0 )
          s.arbiter.reqs[i] @= s.in_[i].val

    # Combinational Logic

    @update
    def up_any_hold():
      s.any_hold @= s.hold > 0

    @update
    def up_granted_val():
      s.granted_val @= 0
      for i in range( s.num_inports ):
        if s.arbiter.grants[i]:
          s.granted_val @= s.in_[i].val

    for i in range( s.num_inports ):
      s.in_[i].msg //= s.mux.in_[i]

  def line_trace( s ):
    in_trace  = '|'.join( [ str(p) for p in s.in_ ] )
    hold      = ''.join([ '^' if h else '.' for h in s.hold ])
    out_trace = f'{s.out}'

    state = 'Hd' if s.state == s.STATE_HEADER else \
            'SB' if s.state == s.STATE_BODY_STRAIGHT else \
            'NB' if s.state == s.STATE_BODY_NORMAL else \
            '??'

    return f'{in_trace}({s.arbiter.line_trace()}|{state}<{s.mux.sel}>[{s.SPEC_SRC}]){out_trace}'
