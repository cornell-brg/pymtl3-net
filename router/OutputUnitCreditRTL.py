"""
==========================================================================
OutputUnitCreditRTL.py
==========================================================================
An output unit with a credit based interface.

Author : Yanghui Ou
  Date : June 22, 2019
"""
from ocn_pclib.ifcs.CreditIfc import CreditSendIfcRTL
from ocn_pclib.rtl import Counter
from pymtl3 import *
from pymtl3.stdlib.ifcs import GetIfcRTL, enrdy_to_str


class OutputUnitCreditRTL( Component ):

  def construct( s, MsgType, vc=2, credit_line=2 ):
    assert vc > 1

    # Interface
    s.get = GetIfcRTL( MsgType )
    s.send = CreditSendIfcRTL( MsgType, vc )

    s.MsgType = MsgType
    s.vc    = vc

    # Loval types
    credit_type = mk_bits( clog2(credit_line+1) )
    vcid_type   = mk_bits( clog2( vc ) if vc > 1 else 1 )

    s.credit = [ Counter( credit_type, credit_line ) for _ in range( vc ) ]

    s.get.msg //= s.send.msg

    @s.update
    def up_credit_send():
      s.send.en = b1(0)
      s.get.en = b1(0)
      if s.get.rdy:
        # print( str(s) + " : " + str(s.get.msg) )
        for i in range( vc ):
          if vcid_type(i) == s.get.msg.vc_id and s.credit[i].count > credit_type(0):
            s.send.en = b1(1)
            s.get.en = b1(1)

    @s.update
    def up_counter_decr():
      for i in range( vc ):
        s.credit[i].decr = s.send.en & ( vcid_type(i) == s.send.msg.vc_id )

    for i in range( vc ):
      s.credit[i].incr       //= s.send.yum[i]
      s.credit[i].load       //= b1(0)
      s.credit[i].load_value //= credit_type(0)

  def line_trace( s ):
    return "{}({}){}".format(
      s.get,
      ",".join( [ str(s.credit[i].count) for i in range(s.vc) ] ),
      s.send,
    )
