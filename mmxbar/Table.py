'''
==========================================================================
Table.py
==========================================================================
A table data-structure that is used for restoring the opaque field.

Author : Yanghui Ou
Date   : April 10, 2020
'''
from pymtl3 import *

class Table( Component ):

  def construct( s, EntryType, num_entries ):

    # Local parameters

    IdxType = Bits1 if num_entries==1 else mk_bits( clog2( num_entries ) )
    BitsN   = mk_bits( num_entries )

    # Interface

    s.alloc   = CalleeIfcRTL( en=True, rdy=True, MsgType=EntryType, RetType=IdxType )
    s.dealloc = CalleeIfcRTL( en=True, rdy=True, MsgType=IdxType, RetType=EntryType )

    # Components

    s.entry_r = [ Wire( EntryType ) for _ in range( num_entries ) ]
    # s.valid_r = Wire( BitsN )
    s.valid_r = [ Wire( Bits1 ) for _ in range( num_entries )  ]

    s.avail_idx_r    = Wire( IdxType )
    s.avail_idx_next = Wire( IdxType )

    # Logic

    @update_ff
    def up_entry_r_valid_r():
      if s.reset:
        # s.valid_r <<= BitsN(0)
        for i in range( num_entries ):
          s.valid_r[i] <<= 0
      else:
        if s.alloc.en:
          s.entry_r[ s.avail_idx_r ] <<= s.alloc.msg
          s.valid_r[ s.avail_idx_r ] <<= 1

        if s.dealloc.en:
          s.valid_r[ s.dealloc.msg ] <<= 0

    @update
    def up_avail_idx_next():
      s.avail_idx_next @= 0
      for i in range( num_entries ):
        if ~s.valid_r[i] & \
           ~( s.alloc.en & ( s.avail_idx_r == i ) ) | \
           s.dealloc.en & ( s.dealloc.msg == i ):
          s.avail_idx_next @= i

    @update_ff
    def up_avail_idx_r():
      if s.reset:
        s.avail_idx_r <<= IdxType(num_entries-1)
      else:
        s.avail_idx_r <<= s.avail_idx_next

    # rdy signals

    # s.alloc.rdy   //= lambda: ~reduce_and( s.valid_r )
    # s.dealloc.rdy //= lambda: reduce_or( s.valid_r )

    @update
    def up_alloc_rdy():
      s.alloc.rdy @= 0
      for i in range( num_entries ):
        if ~s.valid_r[i]:
          s.alloc.rdy @= 1

    @update
    def up_dealloc_rdy():
      s.dealloc.rdy @= 0
      for i in range( num_entries ):
        if s.valid_r[i]:
          s.dealloc.rdy @= 1

    # ret signals

    s.alloc.ret   //= s.avail_idx_r
    s.dealloc.ret //= lambda: s.entry_r[ s.dealloc.msg ] if s.valid_r[ s.dealloc.msg ] else EntryType(-1)

  def line_trace( s ):
    valid_r = ''.join([ 'v' if x else '.' for x in s.valid_r ])
    return f'{s.alloc}({s.avail_idx_r}<={s.avail_idx_next}|{valid_r}){s.dealloc}'
