#=========================================================================
# enrdy_adapters
#=========================================================================
# Adapters for EnRdy interface
#
# Author : Yanghui Ou
#   Date : Feb 20, 2019

from pymtl import *
from pclib.ifcs import InValRdyIfc, OutValRdyIfc
from pclib.ifcs.EnRdyIfc import InEnRdyIfc, OutEnRdyIfc

#-------------------------------------------------------------------------
# ValRdy2EnRdy
#-------------------------------------------------------------------------

class ValRdy2EnRdy( RTLComponent ):

  def construct( s, MsgType ):

    s.in_ = InValRdyIfc( MsgType )
    s.out = OutEnRdyIfc( MsgType ) 

    @s.update
    def comb_logic0():
      s.in_.rdy = s.out.rdy

    @s.update
    def comb_logic1():
      s.out.en  = s.out.rdy and s.in_.val
    
    @s.update
    def comb_logic2(): 
      s.out.msg = s.in_.msg
  
  def line_trace( s ):

    return "{} | {}".format( s.in_, s.out )

#-------------------------------------------------------------------------
# EnRdy2ValRdy
#-------------------------------------------------------------------------

class EnRdy2ValRdy( RTLComponent ):

  def construct( s, MsgType ):

    s.in_ = InEnRdyIfc  ( MsgType )
    s.out = OutValRdyIfc( MsgType ) 

    @s.update
    def comb_logic0():
      s.in_.rdy = s.out.rdy
    
    @s.update
    def comb_logic1():
      s.out.val = s.in_.en
    
    @s.update
    def comb_logic2(): 
      s.out.msg = s.in_.msg
  
  def line_trace( s ):

    return "{} | {}".format( s.in_, s.out )