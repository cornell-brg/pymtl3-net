'''
==========================================================================
PitonMeshNetValRdy.py
==========================================================================
The openpiton network with val/rdy interface.

Author : Yanghui Ou
  Date : Mar 10, 2020
'''
from pymtl3 import *
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

    # Interface

    s.in_ = [ InValRdyIfc ( Bits64 ) for _ in range( nterminals ) ]
    s.out = [ OutValRdyIfc( Bits64 ) for _ in range( nterminals ) ]

    s.offchip_in  = InValRdyIfc( Bits64 )
    s.offchip_out = OutValRdyIfc( Bits64 )

    # Component

    s.net = PitonMeshNet( PitonPositioin, ncols=ncols, nrows=nrows )

    s.in2send  = [ ValRdy2EnRdy( Bits64 ) for _ in range( nterminals ) ]
    s.recv2out = [ EnRdy2ValRdy( Bits64 ) for _ in range( nterminals ) ]

    s.offchip_in2send  = ValRdy2EnRdy( Bits64 )
    s.offchip_recv2out = EnRdy2ValRdy( Bits64 )

    # Connections

    for i in range( nterminals ):
      s.in_[i]          //= s.in2send[i].in_
      s.in2send[i].send //= s.net.recv[i]

      s.net.send[i]  //= s.recv2out[i].recv
      s.recv2out.out //= s.out[i]

    s.offchip_in           //= s.offchip_in2send.in_
    s.offchip_in2send.send //= s.net.offchip_recv

    s.net.offchip_send     //= s.offchip_recv2out.recv
    s.offchip_recv2out.out //= s.offchip_out

  def line_trace( s ):
    return s.net.line_trace()
