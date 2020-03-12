#=========================================================================
# enrdy_adapters
#=========================================================================
# Adapters for EnRdy interface
#
# Author : Yanghui Ou
#   Date : Feb 20, 2019

from pymtl import *
from pymtl3.stdlib.ifcs import InValRdyIfc, OutValRdyIfc
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL

#-------------------------------------------------------------------------
# InValRdy2Send
#-------------------------------------------------------------------------

class InValRdy2Send( Component ):

  def construct( s, Type ):

    s.in_  = InValRdyIfc( Type )
    s.send = SendIfcRTL ( Type )

    s.in_.rdy  //= s.send.rdy
    s.send.en  //= lambda: s.send.rdy & s.in_.val
    s.send.msg //= s.in_.msg

  def line_trace( s ):
    return f'{s.in_}(){s.send}'

#-------------------------------------------------------------------------
# Recv2OutValRdy
#-------------------------------------------------------------------------

class Recv2OutValRdy( Component ):

  def construct( s, Type ):

    s.recv = RecvIfcRTL  ( Type )
    s.out  = OutValRdyIfc( Type )

    s.recv.rdy //= s.out.rdy
    s.out.val  //= s.recv.en
    s.out.msg  //= s.recv.msg

  def line_trace( s ):
    return f"{s.recv}(){s.out}"
