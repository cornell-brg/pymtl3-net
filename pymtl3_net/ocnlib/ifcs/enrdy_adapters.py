#=========================================================================
# enrdy_adapters
#=========================================================================
# Adapters for EnRdy interface
#
# Author : Yanghui Ou
#   Date : Feb 20, 2019

from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import RecvIfcRTL as InValRdyIfc, SendIfcRTL as OutValRdyIfc
from pymtl3.stdlib.ifcs   import SendIfcRTL, RecvIfcRTL

#-------------------------------------------------------------------------
# InValRdy2Send
#-------------------------------------------------------------------------

class InValRdy2Send( Component ):

  def construct( s, Type ):

    s.recv = InValRdyIfc( Type )
    s.send = SendIfcRTL ( Type )

    s.recv.rdy //= s.send.rdy
    s.send.en  //= lambda: s.send.rdy & s.recv.val
    s.send.msg //= s.recv.msg

  def line_trace( s ):
    return f'{s.recv}(){s.send}'

#-------------------------------------------------------------------------
# Recv2OutValRdy
#-------------------------------------------------------------------------

class Recv2OutValRdy( Component ):

  def construct( s, Type ):

    s.recv = RecvIfcRTL  ( Type )
    s.send = OutValRdyIfc( Type )

    s.recv.rdy //= s.send.rdy
    s.send.val  //= s.recv.en
    s.send.msg  //= s.recv.msg

  def line_trace( s ):
    return f"{s.recv}(){s.send}"
