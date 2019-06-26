"""
==========================================================================
InputUnitCreditRTL.py
==========================================================================
An input unit with a credit based interface.

Author : Yanghui Ou
  Date : June 22, 2019
"""
from pymtl3 import *
from pymtl3.stdlib.ifcs import GiveIfcRTL
from pymtl3.stdlib.rtl.queues import NormalQueueRTL
from pymtl3.stdlib.rtl.Encoder import Encoder
from pymtl3.stdlib.rtl.arbiters import RoundRobinArbiterEn

from ocn_pclib.ifcs.CreditIfc import CreditRecvIfcRTL

class InputUnitCreditRTL( Component ):

  def construct( s, PacketType, QueueType = NormalQueueRTL,
                 nvcs=2, credit_line=2 ):

    # Local paramters
    s.nvcs = nvcs

    # Interface
    s.recv = CreditRecvIfcRTL( PacketType, nvcs=nvcs )
    s.give = [ GiveIfcRTL( PacketType ) for _ in range( nvcs ) ]

    # Component
    VcIDType   = mk_bits( clog2( nvcs ) if nvcs > 1 else 1 )

    s.buffers = [ QueueType( PacketType, num_entries=credit_line )
                  for _ in range( nvcs ) ]

    for i in range( nvcs ):
      s.connect( s.buffers[i].enq.msg, s.recv.msg )
      s.connect( s.buffers[i].deq,     s.give[i]  )

    @s.update
    def up_enq():
      if s.recv.en:
        for i in range( nvcs ):
          s.buffers[i].enq.en = s.recv.msg.vc_id == VcIDType(i)
          if s.buffers[i].enq.en: assert s.buffers[i].enq.rdy, "{}: buffer[{}] enable when not rdy!".format( s, i )
      else:
        for i in range( nvcs ):
          s.buffers[i].enq.en = b1(0)

    @s.update
    def up_yummy():
      for i in range( nvcs ):
        s.recv.yum[i] = s.buffers[i].deq.en

  def line_trace( s ):
    return "{}({}){}".format(
      s.recv,
      ",".join([ str( s.buffers[i].count ) for i in range( s.nvcs ) ]),
      "|".join([ str(s.give[i]) for i in range( s.nvcs ) ]),
    )
