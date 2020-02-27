'''
==========================================================================
SerializerRTL.py
==========================================================================
A generic serializer unit.

Author : Yanghui Ou
  Date : Feb 25, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from pymtl3.stdlib.rtl import Mux

from .Counter import Counter

class SerializerRTL( Component ):

  #-----------------------------------------------------------------------
  # Construct
  #-----------------------------------------------------------------------

  def construct( s, out_nbits, max_nblocks ):

    # Local parameter

    s.InType    = mk_bits( out_nbits*( max_nblocks ) )
    s.OutType   = mk_bits( out_nbits )
    s.CountType = mk_bits( clog2( max_nblocks+1 ) )

    s.STATE_IDLE = b1(0)
    s.STATE_SEND = b1(1)

    s.sel_nbits = clog2( max_nblocks )

    # Interface

    s.recv = RecvIfcRTL( s.InType    )
    s.send = SendIfcRTL( s.OutType   )
    s.len  = InPort    ( s.CountType )

    # Components

    s.state      = Wire( Bits1       )
    s.state_next = Wire( Bits1       )
    s.in_r       = Wire( s.InType    )
    s.len_r      = Wire( s.CountType )

    s.counter    = Counter( s.CountType )( decr=b1(0) )
    s.mux        = Mux( s.OutType, max_nblocks )

    # Input register

    @s.update_ff
    def up_in_r():
      if s.recv.en & ( s.state_next != s.STATE_IDLE ):
        s.in_r  <<= s.recv.msg
        # Force len to 1 if it is set to be 0 to avoid undefined behavior
        s.len_r <<= s.len if s.len > s.CountType(0) else s.CountType(1)
      else:
        s.in_r  <<= s.in_r
        s.len_r <<= s.CountType(0) if s.state_next == s.STATE_IDLE else s.len_r

    # Mux logic

    for i in range( max_nblocks ):
      s.mux.in_[i] //= s.in_r[ i*out_nbits : (i+1)*out_nbits ]
    s.mux.sel //= s.counter.count[0:s.sel_nbits]

    # Counter load

    s.counter.load //= lambda: s.recv.en | ( s.state_next == s.STATE_IDLE )
    s.counter.incr //= lambda: s.send.en & ( s.state_next != s.STATE_IDLE )

    @s.update
    def up_counter_load_value():
      if ( s.state == s.STATE_IDLE ) & s.send.rdy & ( s.state_next != s.STATE_IDLE ):
        s.counter.load_value = s.CountType(1)
      else:
        s.counter.load_value = s.CountType(0)

    # Recv logic

    s.recv.rdy //= lambda: s.state == s.STATE_IDLE
    
    # Send logic

    @s.update
    def up_send_msg():
      if ( s.state == s.STATE_IDLE ) & s.recv.en & s.send.rdy:
        s.send.msg = s.recv.msg[0:out_nbits]
      else:
        s.send.msg = s.mux.out

    @s.update
    def up_send_en():
      if ( s.state == s.STATE_IDLE ) & s.recv.en & s.send.rdy | \
         ( s.state == s.STATE_SEND ) & s.send.rdy:
        s.send.en = b1(1)
      else:
        s.send.en = b1(0)

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
        # If length is 1, bypass to IDLE
        if ( s.len == s.CountType(1) ) & s.send.en:
          s.state_next = s.STATE_IDLE

        elif s.recv.en:
          s.state_next = s.STATE_SEND
          print( s.state_next )

        else:
          s.state_next = s.STATE_IDLE

      else: # STATE_SEND
        if ( s.counter.count == s.len_r - s.CountType(1) ) & s.send.rdy:
          s.state_next = s.STATE_IDLE
        else:
          s.state_next = s.STATE_SEND

  #-----------------------------------------------------------------------
  # line trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    state = 'I' if s.state == s.STATE_IDLE else \
            'S' if s.state == s.STATE_SEND else \
            '?'
    state_next = 'I' if s.state_next == s.STATE_IDLE else \
            'S' if s.state_next == s.STATE_SEND else \
            '?'
    return f'{s.recv}({state}{s.counter.count}<{s.len_r}){s.send}'
