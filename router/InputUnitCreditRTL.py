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
                 vc=2, credit_line=2 ):

    # Local paramters
    s.vc = vc

    # Interface
    s.recv = CreditRecvIfcRTL( PacketType, vc=vc )
    s.give = [ GiveIfcRTL( PacketType ) for _ in range( vc ) ]

    # Component
    VcIDType = mk_bits( clog2( vc ) ) if vc > 1 else Bits1

    s.buffers = [ QueueType( PacketType, num_entries=credit_line )
                  for _ in range( vc ) ]

    for i in range( vc ):
      s.buffers[i].enq.msg //= s.recv.msg
      s.buffers[i].deq     //= s.give[i]
      s.recv.yum[i]        //= s.give[i].en

    @s.update
    def up_enq():
      if s.recv.en:
        for i in range( vc ):
          s.buffers[i].enq.en = s.recv.msg.vc_id == VcIDType(i)
      else:
        for i in range( vc ):
          s.buffers[i].enq.en = b1(0)

  def line_trace( s ):
    return "{}({}){}".format(
      s.recv,
      ",".join([ str(s.buffers[i].count) for i in range( s.vc ) ]),
      "|".join([ str(s.give[i]) for i in range( s.vc ) ]),
    )
