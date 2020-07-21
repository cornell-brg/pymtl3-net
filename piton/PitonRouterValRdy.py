'''
==========================================================================
PitonRouterValRdy.py
==========================================================================
A wrapper around PitonRouter that has val/rdy interfaces.

Author : Yanghui Ou
  Date : Jun 3, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs import InValRdyIfc, OutValRdyIfc
from pymtl3.passes.backends.verilog import *

from ocnlib.ifcs.enrdy_adapters import InValRdy2Send, Recv2OutValRdy

from .PitonRouter import PitonRouter

#-------------------------------------------------------------------------
# PitonRouterValRdy
#-------------------------------------------------------------------------

class PitonRouterValRdy( Component ):

  def construct( s, PositionType ):

    # Metadata

    s.set_metadata( VerilogTranslationPass.explicit_module_name, f'pyocn_router' )

    # Interface

    s.in_ = [ InValRdyIfc ( Bits64 ) for _ in range(5) ]
    s.out = [ OutValRdyIfc( Bits64 ) for _ in range(5) ]
    s.pos = InPort( PositionType )

    # Component

    s.in2send  = [ InValRdy2Send ( Bits64 ) for _ in range(5) ]
    s.recv2out = [ Recv2OutValRdy( Bits64 ) for _ in range(5) ]
    s.router   = PitonRouter( PositionType )

    # Connections

    s.pos //= s.router.pos

    for i in range(5):
      s.in_[i]          //= s.in2send[i].in_
      s.in2send[i].send //= s.router.recv[i]
      s.router.send[i]  //= s.recv2out[i].recv
      s.recv2out[i].out //= s.out[i]

  def line_trace( s ):
    return s.router.line_trace()

