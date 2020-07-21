'''
==========================================================================
DummyNode.py
==========================================================================
A dummy node that acts like a terminal. This should be connected to the
terminal interface of the router to avoid the pin placement issue in
physical design flow.

Author: Yanghui Ou
  Date: Jun 19, 2020
'''

from pymtl3 import *
from pymtl3.stdlib.basic_rtl import RegisterFile
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL


class DummyNode( Component ):

  def construct( s, Header ):

    # Local parameter

    s.PhitType = mk_bits( Header.nbits )

    # Interface

    s.send = SendIfcRTL( Header )
    s.recv = RecvIfcRTL( Header )

    # Regs and wires

    s.addr_r     = Wire( Bits5 )
    s.recv_rdy_r = Wire( Bits1 )

    # Component

    s.reg_file = RegisterFile( Header, nregs=32 )
    s.reg_file.raddr[0] //= s.addr_r
    s.reg_file.waddr[0] //= s.addr_r

    # Sequential logic

    @update_ff
    def up_addr():
      if s.reset:
        s.addr_r <<= 0
      elif s.recv.en:
        s.addr_r <<= s.addr_r + 1 if s.addr_r != 31 else 0
      else:
        s.addr_r <<= s.addr_r

    @update_ff
    def up_recv_rdy_r():
      if s.reset:
        s.recv_rdy_r <<= 0
      else:
        s.recv_rdy_r <<= ~s.recv_rdy_r

    s.send.en  //= s.send.rdy
    s.send.msg //= s.reg_file.rdata[0]

    s.recv.rdy //= s.recv_rdy_r
    s.recv.msg //= s.reg_file.wdata[0]

  def line_trace( s ):
    return f'{s.recv}(){s.send}'
