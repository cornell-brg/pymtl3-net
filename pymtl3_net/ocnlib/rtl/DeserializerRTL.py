'''
==========================================================================
DeserializerRTL.py
==========================================================================
A Generic deserializer.

Author : Yanghui Ou
  Date : Feb 26, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs import IStreamIfc, OStreamIfc

from .Counter import Counter

class DeserializerRTL( Component ):

  #-----------------------------------------------------------------------
  # construct
  #-----------------------------------------------------------------------

  def construct( s, in_nbits, max_nblocks ):

    # Local parameter

    InType    = mk_bits( in_nbits )
    OutType   = mk_bits( in_nbits * max_nblocks )
    CountType = mk_bits( clog2( max_nblocks +1 ) )
    SelType   = mk_bits( clog2( max_nblocks ) )

    s.STATE_IDLE = 0
    s.STATE_RECV = 1

    # Interface

    s.recv = IStreamIfc( InType    )
    s.len  = InPort    ( CountType )
    s.send = OStreamIfc( OutType   )

    # Component

    s.state      = Wire()
    s.state_next = Wire()
    s.idx        = Wire( CountType )
    s.len_r      = Wire( CountType )
    s.out_r      = [ Wire( InType ) for _ in range( max_nblocks ) ]
    s.counter    = Counter( CountType )

    s.counter.decr  //= 0
    s.counter.count //= s.idx

    # Input register

    @update_ff
    def up_len_r():
      if ( s.state == s.STATE_IDLE ) & s.recv.en | \
         ( s.state == s.STATE_RECV ) & ( s.idx == s.len_r ) & s.send.en:
        s.len_r <<= s.len if s.len > 0 else 1
      else:
        if s.state_next == s.STATE_IDLE:
          s.len_r <<= 0

    # Reg write logic

    @update_ff
    def up_out_r():
      if s.reset:
        for i in range( max_nblocks ):
          s.out_r[i] <<= InType(0)

      elif ( s.state == s.STATE_RECV ) & ( s.idx == s.len_r ) & s.send.en:
        if s.recv.en:
          s.out_r[0] <<= s.recv.msg
        else:
          s.out_r[0] <<= 0
        for i in range(1, max_nblocks):
          s.out_r[i] <<= 0

      elif s.recv.en:
        s.out_r[ trunc(s.idx, SelType) ] <<= s.recv.msg

    for i in range( max_nblocks ):
      s.send.msg[i*in_nbits:(i+1)*in_nbits] //= s.out_r[i]

    # Counter logic

    s.counter.incr //= s.recv.en

    # Recv/Send logic

    s.send.en //= lambda: ( s.state == s.STATE_RECV ) & ( s.idx ==  s.len_r ) & s.send.rdy

    @update
    def up_recv_rdy():
      if s.state == s.STATE_IDLE:
        s.recv.rdy @= 1

      else: # STATE_RECV
        if s.idx < s.len_r:
          s.recv.rdy @= 1
        elif s.send.en:
          s.recv.rdy @= 1

        else:
          s.recv.rdy @= 0

    # State transition logic

    @update_ff
    def up_state():
      if s.reset:
        s.state <<= s.STATE_IDLE
      else:
        s.state <<= s.state_next

    @update
    def up_state_next():
      if s.state == s.STATE_IDLE:
        if ( s.len > 0 ) & s.recv.en:
          s.state_next         @= s.STATE_RECV
          s.counter.load       @= 1
          s.counter.load_value @= 1

        else:
          s.state_next         @= s.STATE_IDLE
          s.counter.load       @= 0
          s.counter.load_value @= CountType(0)

      else: # STATE_RECV
        if ( s.idx == s.len_r ) & s.send.en:
          if s.recv.en:
            s.state_next         @= s.STATE_RECV
            s.counter.load       @= 1
            s.counter.load_value @= 1
          else:
            s.state_next         @= s.STATE_IDLE
            s.counter.load       @= 1
            s.counter.load_value @= 0

        else:
          s.state_next         @= s.STATE_RECV
          s.counter.load       @= 0
          s.counter.load_value @= 0

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    state = 'I' if s.state == s.STATE_IDLE else \
            'R' if s.state == s.STATE_RECV else \
            '?'
    return f'{s.recv}({state}:{s.idx}<{s.len_r}){s.send}'
