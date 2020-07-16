'''
==========================================================================
PitonMeshNetValRdy.py
==========================================================================
The openpiton network with val/rdy interface.

Author : Yanghui Ou
  Date : Mar 10, 2020
'''
from pymtl3 import *
from pymtl3.passes.backends.verilog import *
from pymtl3.stdlib.ifcs import InValRdyIfc, OutValRdyIfc
from ocnlib.ifcs.enrdy_adapters import InValRdy2Send, Recv2OutValRdy

from .PitonMeshNet import PitonMeshNet

@bitstruct
class PitonPosition:
  pos_x : Bits8
  pos_y : Bits8

class PitonMeshNetValRdy( Component ):

  def construct( s, ncols=2, nrows=7 ):

    # Local prameter

    nterminals = ncols * nrows
    s.set_metadata( VerilogTranslationPass.explicit_module_name, f'pyocn_mesh_{ncols}x{nrows}' )

    # Interface

    s.in_ = [ InValRdyIfc ( Bits64 ) for _ in range( nterminals ) ]
    s.out = [ OutValRdyIfc( Bits64 ) for _ in range( nterminals ) ]

    s.offchip_in  = InValRdyIfc( Bits64 )
    s.offchip_out = OutValRdyIfc( Bits64 )

    # Component

    s.net = PitonMeshNet( PitonPosition, ncols=ncols, nrows=nrows )

    s.in2send  = [ InValRdy2Send( Bits64 ) for _ in range( nterminals ) ]
    s.recv2out = [ Recv2OutValRdy( Bits64 ) for _ in range( nterminals ) ]

    s.offchip_in2send  = InValRdy2Send( Bits64 )
    s.offchip_recv2out = Recv2OutValRdy( Bits64 )

    # Connections

    for i in range( nterminals ):
      s.in_[i]          //= s.in2send[i].in_
      s.in2send[i].send //= s.net.recv[i]

      s.net.send[i]     //= s.recv2out[i].recv
      s.recv2out[i].out //= s.out[i]

    s.offchip_in           //= s.offchip_in2send.in_
    s.offchip_in2send.send //= s.net.offchip_recv

    s.net.offchip_send     //= s.offchip_recv2out.recv
    s.offchip_recv2out.out //= s.offchip_out

  def line_trace( s ):
    return s.net.line_trace()
