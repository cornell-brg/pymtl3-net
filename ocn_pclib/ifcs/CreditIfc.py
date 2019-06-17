"""
==========================================================================
 CreditIfc.py
==========================================================================
Credit based interfaces.

Author : Yanghui Ou
  Date : June 10, 2019
"""
from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL, enrdy_to_str
from pymtl3.stdlib.rtl import Encoder
from pymtl3.stdlib.rtl.arbiters import RoundRobinArbiterEn
from pymtl3.stdlib.rtl.queues import BypassQueueRTL

from ocn_pclib.rtl import Counter

class CreditRecvIfcRTL( Interface ):

  def construct( s, MsgType, nvcs=1 ):
    assert nvcs > 1, "We only support multiple virtual channels!"

    s.en  = InPort ( Bits1   )
    s.msg = InPort ( MsgType )
    s.yum = [ OutPort( Bits1   ) for i in range( nvcs ) ]

    s.MsgType = MsgType
    s.nvcs    = nvcs

  def __str__( s ):
    try:
      trace_len = s.trace_len
    except AttributeError:
      s.trace_len = len( str(s.MsgType()) )
      trace_len = s.trace_len
    return "{},{}".format(
      enrdy_to_str( s.msg, s.en, True, s.trace_len ),
      "".join( [ "$" if x else '.' for x in s.yum ] )
    )

class CreditSendIfcRTL( Interface ):

  def construct( s, MsgType, nvcs=1 ):
    assert nvcs > 1, "We only support multiple virtual channels!"

    s.en  = OutPort( Bits1   )
    s.msg = OutPort( MsgType )
    s.yum = [ InPort ( Bits1   ) for _ in range( nvcs ) ]

    s.MsgType = MsgType
    s.nvcs    = nvcs

  def __str__( s ):
    try:
      trace_len = s.trace_len
    except AttributeError:
      s.trace_len = len( str(s.MsgType()) )
      trace_len = s.trace_len
    return "{},{}".format(
      enrdy_to_str( s.msg, s.en, True, s.trace_len ),
      "".join( [ "$" if s.yum[i] else '.' for i in range(s.nvcs) ] )
    )

class CreditSendIfcCL( Interface ):

  def construct( s, MsgType, nvcs=1 ):
    assert nvcs > 1, "We only support multiple virtual channels!"

    s.send_msg    = CallerPort( MsgType )
    s.recv_credit = [ CalleePort() for _ in range( nvcs ) ]

    s.MsgType = MsgType
    s.nvcs    = nvcs

  def __str__( s ):
    return ""

class CreditRecvIfcCL( Interface ):

  def construct( s, MsgType, nvcs=1 ):
    assert nvcs > 1, "We only support multiple virtual channels!"

    s.recv_msg    = CalleePort( MsgType )
    s.send_credit = [ CallerPort() for _ in range( nvcs ) ]

    s.MsgType = MsgType
    s.nvcs    = nvcs

  def __str__( s ):
    return ""


#-------------------------------------------------------------------------
# CreditIfc adapters
#-------------------------------------------------------------------------

class RecvRTL2CreditSendRTL( Component ):

  def consrtuct( s, MsgType, nvcs=2, credit_line=1 ):
    assert nvcs > 1

    # Interface

    s.recv = RecvIfcRTL( MsgType )
    s.send = CreditSendIfcRTL( MsgType, nvcs )

    s.MsgType = MsgType
    s.nvcs    = nvcs
    
    # Components

    CreditType = mk_bits( clog2(credit_line+1) )
    VcIDType   = mk_bits( clog2( nvcs ) if nvcs > 1 else 1 )
    
    s.buffer = BypassQueueRTL( MsgType, num_entries=1 )
    s.credit = [ Counter( CreditType, credit_line ) for _ in range( nvcs ) ]

    s.connect( s.recv,           s.buffer.enq )
    s.connect( s.buffer.deq.msg, s.send.msg   )

    @s.update
    def up_credit_send():
      s.send.en = b1(0)
      for i in range( nvcs ):
        if VcIDType(i) == s.buffer.deq.msg.vc_id and \
           s.credit[i].count > CreditType(0):
          s.send.en = b1(1)
    
    @s.update
    def up_counter_decr():
      for i in range( nvcs ):
        s.credit[i].decr = s.send.en & ( VcIDType(i) == s.send.msg.vc_id )

    for i in range( nvcs ):
      s.connect( s.credit[i].incr,       s.send.yum[i] )
      s.connect( s.credit[i].load,       b1(0)         )
      s.connect( s.credit[i].load_value, CreditType(0) )

  def line_trace( s ):
    return "{}({}){}".format(
      s.recv,
      ",".join( [ str(s.credit[i].count) for i in range(s.nvcs) ] ),
      s.send,
    )

class CreditRecvRTL2SendRTL( Component ):

  def consrtuct( s, MsgType, nvcs=2, credit_line=1 ):
    assert nvcs > 1

    # Interface

    s.recv = CreditRecvIfcRTL( MsgType )
    s.send = SendIfcRTL( MsgType, nvcs )

    s.MsgType = MsgType
    s.nvcs    = nvcs

    # Components

    CreditType = mk_bits( clog2(credit_line+1) )
    ArbReqType = mk_bits( nvcs )
    VcIDType   = mk_bits( clog2( nvcs ) if nvcs > 1 else 1 )

    s.buffers = [ BypassQueueRTL( MsgType, num_entries=credit_line ) 
                  for _ in range( nvcs ) ]
    s.arbiter = RoundRobinArbiterEn( nreqs=nvcs )
    s.encoder = Encoder( in_nbits=nvcs, out_nbits=clog2(nvcs) )

    for i in range( nvcs ):
      s.connect( s.buffers[i].deq.rdy, s.arbiter.reqs[i] )
    s.connect( s.arbiter.grants, s.encoder.in_ )
    s.connect( s.arbiter.en,     s.send.en     )

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