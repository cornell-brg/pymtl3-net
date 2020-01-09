'''
==========================================================================
NetRecv2AXI4Slave.py
==========================================================================
Adapter that converts network packets to AXI4 transaction.

Author : Yanghui Ou
  Date : Jan 9, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from pymtl3.rtl.queues import NormalQueueRTL

from .axi4_msgs import *

class NetRecv2AXI4Slave( Component ):

  def construct( s, PktType, xpos=0, ypos=0 ):

    # AXI4 slave interface

    s.read_data  = SendIfcRTL( AXI4DataRead )
    s.write_resp = SendIfcRTL( AXI4WriteResp )

    # Network interface

    s.net_recv = RecvIfcRTL( PktType )

    # Constants

    s.HEADER = b1(0)
    s.DATA   = b1(1)

    # Registers

    s.state = Wire( Bits1 )

    # Wires

    # Components

    s.in_q = NormalQueueRTL( PktType, num_entries=2 )( enq = s.net_recv )

    # Logic

    @s.update
    def up_deq_send():
      if s.in_q.deq.rdy:
        ...
      else:
        s.read_data.en  = b1(0)
        s.write_resp.en = b1(0)
  
    @s.update
    def up_read_data_msg():
      ...

    @s.update
    def up_read_data_msg():
      ...
