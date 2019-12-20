#=========================================================================
# enrdy_adapters
#=========================================================================
# Adapters for EnRdy interface
#
# Author : Yanghui Ou
#   Date : Feb 20, 2019

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL, InValRdyIfc, OutValRdyIfc

#-------------------------------------------------------------------------
# ValRdy2EnRdy
#-------------------------------------------------------------------------

class ValRdy2EnRdy( Component ):

  def construct( s, MsgType ):

    s.in_ = InValRdyIfc( MsgType )
    s.out = SendIfcRTL( MsgType )

    @s.update
    def comb_logic0():
      s.in_.rdy = s.out.rdy

    @s.update
    def comb_logic1():
      s.out.en  = s.out.rdy and s.in_.val
      s.out.msg = s.in_.msg

  def line_trace( s ):

    return f"{s.in_}(){s.out}"

#-------------------------------------------------------------------------
# EnRdy2ValRdy
#-------------------------------------------------------------------------

class EnRdy2ValRdy( Component ):

  def construct( s, MsgType ):

    s.in_ = RecvIfcRTL  ( MsgType )
    s.out = OutValRdyIfc( MsgType )

    @s.update
    def comb_logic0():
      s.in_.rdy = s.out.rdy

    @s.update
    def comb_logic1():
      s.out.val = s.in_.en
      s.out.msg = s.in_.msg

  def line_trace( s ):

    return f"{s.in_}(){s.out}"
