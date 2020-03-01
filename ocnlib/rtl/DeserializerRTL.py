'''
==========================================================================
DeserializerRTL.py
==========================================================================
A Generic deserializer.

Author : Yanghui Ou
  Date : Feb 26, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL

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

    s.STATE_IDLE = b1(0)
    s.STATE_RECV = b1(1)

    # Interface

    s.recv = RecvIfcRTL( InType    )
    s.len  = InPort    ( CountType )
    s.send = SendIfcRTL( OutType   )

    # Component

    s.state      = Wire( Bits1 )
    s.state_next = Wire( Bits1 )
    s.idx        = Wire( CountType )
    s.len_r      = Wire( CountType )
    s.out_r      = [ Wire( InType ) for _ in range( max_nblocks ) ]
    s.counter    = Counter( CountType )( decr=b1(0) )

    s.idx //= s.counter.count

    # Input register

    @s.update_ff
    def up_len_r():
      if s.recv.en & ( s.state == s.STATE_IDLE ) | \
         s.recv.en & ( s.state == s.STATE_RECV ):
        s.len_r <<= s.len if s.len > CountType(0) else CountType(1)
      else:
        s.len_r <<= CountType(0) if s.state_next == s.STATE_IDLE else s.len_r

    # Reg write logic

    @s.update_ff
    def up_out_r():
      if s.reset:
        for i in range( max_nblocks ):
          s.out_r[i] <<= InType(0)

      elif ( s.state == s.STATE_RECV ) & ( s.idx == s.len_r ) & s.send.en: 
        if s.recv.en:
          s.out_r[0] <<= s.recv.msg
        else:
          s.out_r[0] <<= InType(0)
        for i in range(1, max_nblocks):
          s.out_r[i] <<= InType(0)

      elif s.recv.en:
        s.out_r[ s.idx ] <<= s.recv.msg

    for i in range( max_nblocks ):
      s.send.msg[i*in_nbits:(i+1)*in_nbits] //= s.out_r[i]

    # Counter logic

    s.counter.incr //= s.recv.en

    # Recv/Send logic

    s.send.en  //= lambda: ( s.state == s.STATE_RECV ) & ( s.idx ==  s.len_r ) & s.send.rdy

    @s.update
    def up_recv_rdy():
      if s.state == s.STATE_IDLE:
        s.recv.rdy = b1(1)

      else: # STATE_RECV
        if s.idx < s.len_r:
          s.recv.rdy = b1(1)
        elif s.send.en:
          s.recv.rdy = b1(1)

        else:
          s.recv.rdy = b1(0)

    # State transition logic

    @s.update_ff
    def up_state():
      if s.reset:
        s.state <<= s.STATE_IDLE
      else:
        s.state <<= s.state_next

    @s.update
    def up_state_next():
      if s.state == s.STATE_IDLE:
        if ( s.len > CountType(0) ) & s.recv.en:
          s.state_next         = s.STATE_RECV
          s.counter.load       = b1(1)
          s.counter.load_value = CountType(1)

        else:
          s.state_next   = s.STATE_IDLE
          s.counter.load = b1(0)

      else: # STATE_RECV
        if ( s.idx == s.len_r ) & s.send.en: 
          if s.recv.en:
            s.state_next         = s.STATE_RECV
            s.counter.load       = b1(1)
            s.counter.load_value = CountType(1)
          else:
            s.state_next         = s.STATE_IDLE
            s.counter.load       = b1(1)
            s.counter.load_value = CountType(0)

        else:
          s.state_next         = s.STATE_RECV
          s.counter.load       = b1(0)
          s.counter.load_value = CountType(0)

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    state = 'I' if s.state == s.STATE_IDLE else \
            'R' if s.state == s.STATE_RECV else \
            '?'
    return f'{s.recv}({state}:{s.idx}<{s.len_r}){s.send}'
