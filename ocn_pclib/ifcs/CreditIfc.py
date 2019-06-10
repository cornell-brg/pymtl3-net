"""
==========================================================================
 CreditIfc.py
==========================================================================
Credit based interfaces.

Author : Yanghui Ou
  Date : June 10, 2019
"""
from pymtl3 import *

class CreditRecvIfcRTL( Interface ):

  def construct( s, MsgType ):

    s.en  = InPort ( Bits1   )
    s.msg = InPort ( MsgType )
    s.yum = OutPort( Bits1   )

    s.MsgType = MsgType

  # TODO: implement line trace.
  def __str__( s ):
    return ""

class CreditSendIfcRTL( Interface ):

  def construct( s, MsgType ):

    s.en  = OutPort( Bits1   )
    s.msg = OutPort( MsgType )
    s.yum = InPort ( Bits1   )

    s.MsgType = MsgType

  # TODO: implement line trace.
  def __str__( s ):
    return ""
