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

from ocn_pclib.ifcs import CreditRecvIfcRTL

class InputUnitCreditRTL( Component ):

  def construct( s, PacketType, QueueType = NormalQueueRTL,
                 nvcs=2, credit_line=2 ):

    # Interface
    s.recv = CreditRecvIfcRTL( PacketType, nvcs=nvcs )
    s.give = GiveIfcRTL( PacketType )

    # Component
    ArbReqType = mk_bits( nvcs )
    VcIDType   = mk_bits( clog2( nvcs ) if nvcs > 1 else 1 )

    s.buffers = [ QType( MsgType, num_entries=credit_line )
                  for _ in range( nvcs ) ]
    s.arbiter = RoundRobinArbiterEn( nreqs=nvcs )
    s.encoder = Encoder( in_nbits=nvcs, out_nbits=clog2(nvcs) )

    for i in range( nvcs ):
      s.connect( s.buffers[i].enq.msg, s.recv.msg        )
      s.connect( s.buffers[i].deq.rdy, s.arbiter.reqs[i] )
    s.connect( s.arbiter.grants, s.encoder.in_ )
    s.connect( s.arbiter.en,     s.send.en     )

    @s.update
    def up_enq():
      if s.recv.en:
        for i in range( nvcs ):
          s.buffers[i].enq.en = s.recv.msg.vc_id == VcIDType(i)
      else:
        for i in range( nvcs ):
          s.buffers[i].enq.en = b1(0)

    @s.update
    def up_deq_and_send():
      for i in range( nvcs ):
        s.buffers[i].deq.en = b1(0)

      s.send.msg = s.buffers[ s.encoder.out ].deq.msg
      if s.send.rdy & ( s.arbiter.grants > ArbReqType(0) ):
        s.send.en = b1(1)
        s.buffers[ s.encoder.out ].deq.en = b1(1)
      else:
        s.send.en = b1(0)

    @s.update
    def up_yummy():
      for i in range( nvcs ):
        s.recv.yum[i] = s.buffers[i].deq.en

  def line_trace( s ):
    return "{}(){}".format( s.recv, s.send )