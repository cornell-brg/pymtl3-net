'''
==========================================================================
NetSend2AXI4Master
==========================================================================
An adapter that converts network packets into axi4 requests.

Author : Yanghui Ou
  Date : Jan 9, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL

from .axi4_msgs import *

class AXI4Slave2NetSend( Component ):

  def construct( s, PktType ):

    # AXI4 master interface

    s.read_addr = SendIfcRTL( AXI4AddrRead )

    s.write_addr = SendIfcRTL( AXI4AddrRead )
    s.wirte_data = SendIfcRTL( AXI4AddrRead )

    # Network interface

    s.net_recv = RecvIfcRTL( PktType )

    # Constants

    s.HEADER = b2(0)
    s.ADDR   = b2(1)
    s.DATA   = b2(2)

    # Registers

    s.state   = Wire( Bits2 )
    s.dst_x_r = Wire( Bits2 )
    s.dst_y_r = Wire( Bits2 )

    s.is_rd_r  = Wire( Bits1  )
    s.is_wr_r  = Wire( Bits1  )
    s.len_r    = Wire( Bits8  )
    # s.rd_req_r = Wire( AXI4AddrRead  )
    # s.wr_req_r = Wire( AXI4AddrWrite )

    # Wires

    s.state_next = Wire( Bits2 )

    # Logic

