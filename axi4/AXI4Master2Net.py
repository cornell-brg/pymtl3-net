'''
==========================================================================
AXI4Slave2Net.py
==========================================================================
Adapter that converts AXI4 transaction to mesh network packets. We use
arid and awid to inidicate the destination terminal.

NOTE: This component assumes a read and write request never arrives at the
same time.

Author : Yanghui Ou
  Date : Jan 08, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL, RecvIfcRTL
from ocn_pclib.ifcs.packets import mk_mesh_pkt

from .axi4_msgs import *

class AXI4Slave2Net( Component ):

  def construct( s, PktType, xpos=0, ypos=0 ):

    # AXI Slave interface

    s.read_addr = RecvIfcRTL( AXI4AddrRead )
    s.read_data = SendIfcRTL( AXI4DataRead )

    s.write_addr = RecvIfcRTL( AXI4AddrWrite )
    s.write_data = RecvIfcRTL( AXI4DataWrite )
    s.write_resp = SendIfcRTL( AXI4WriteResp )

    # Network interface

    s.net_send = SendIfcRTL( PktType )
    s.net_recv = SendIfcRTL( PktType )

    # Constants

    s.HEADER = b1(0) # Assemble header packet
    s.ADDR   = b1(1) # Assemble addr packet 
    s.DATA   = b1(2) # Assemble body packet

    s.xpos   = b3( xpos )
    s.ypos   = b3( ypos )

    # Registers

    s.state    = Wire( Bits2  )
    s.dst_x    = Wire( Bits3  )
    s.dst_y    = Wire( Bits3  )

    s.rd_req   = Wire( Bits1  )
    s.wr_req   = Wire( Bits1  )
    s.data_len = Wire( Bits8  )
    s.addr_reg = Wire( Bits64 )

    # Wires

    s.state_next = Wire( Bits2 )

    # Logic

    s.read_addr.rdy  //= lambda: ( s.state == s.HEADER ) & s.net_send.rdy
    s.write_addr.rdy //= lambda: ( s.state == s.HEADER ) & s.net_send.rdy
    s.write_data.rdy //= lambda: ( s.state == s.DATA   ) & s.net_send.rdy

    @s.update_ff
    def up_state():
      if s.reset:
        s.state <<= s.HEADER
      else:
        s.state <<= s.state_next

    @s.update
    def up_state_transition():
      if s.state == s.HEADER:
        if s.net_send.en:
          s.state_next = s.ADDR
        else:
          s.state_next = s.HEADER

      elif s.state == s.ADDR:
        if s.net_send.en & s.wr_req:
          s.state_next = s.DATA
        elif s.net_send.en & s.rd_req:
          s.state_next = s.HEADER
        else:
          s.state_next = s.ADDR

      else: # s.state == s.DATA
        if ( s.data_len == b8(1) ) & s.net_send.en:
          s.state_next = s.HEADER
        else:
          s.state_next = s.DATA

    s.net_send.msg.src_x //= s.xpos
    s.net_send.msg.src_y //= s.ypos

    @s.update
    def up_dst_pos():
      ...

    @s.update
    def up_payload():
      if s.state == s.HEADER:

        # Assembles a read request
        if s.read_addr.en:
          s.noc_send.msg.payload[ MTYPE  ] = TYPE_RD
          s.noc_send.msg.payload[ LEN    ] = s.read_addr.msg.arlen
          s.noc_send.msg.payload[ SIZE   ] = s.read_addr.msg.arsize
          s.noc_send.msg.payload[ BURST  ] = s.read_addr.msg.arburst
          s.noc_send.msg.payload[ LOCK   ] = s.read_addr.msg.arlock
          s.noc_send.msg.payload[ CACHE  ] = s.read_addr.msg.arcache
          s.noc_send.msg.payload[ PROT   ] = s.read_addr.msg.arprot
          s.noc_send.msg.payload[ QOS    ] = s.read_addr.msg.arqos
          s.noc_send.msg.payload[ REGION ] = s.read_addr.msg.arregion
          s.noc_send.msg.payload[ REUSER ] = s.read_addr.msg.aruser

        # Assembles a write request
        elif s.write_addr.en:
          s.noc_send.msg.payload[ MTYPE  ] = TYPE_WR
          s.noc_send.msg.payload[ LEN    ] = s.write_addr.msg.awlen
          s.noc_send.msg.payload[ SIZE   ] = s.write_addr.msg.awsize
          s.noc_send.msg.payload[ BURST  ] = s.write_addr.msg.awburst
          s.noc_send.msg.payload[ LOCK   ] = s.write_addr.msg.awlock
          s.noc_send.msg.payload[ CACHE  ] = s.write_addr.msg.awcache
          s.noc_send.msg.payload[ PROT   ] = s.write_addr.msg.awprot
          s.noc_send.msg.payload[ QOS    ] = s.write_addr.msg.awqos
          s.noc_send.msg.payload[ REGION ] = s.write_addr.msg.awregion
          s.noc_send.msg.payload[ REUSER ] = s.write_addr.msg.awuser

        else:
          s.noc_send.msg.payload = b64(0)
          
      elif s.state == s.ADDR:
        s.net_send.msg.payload = s.addr_reg

      else: # s.state == s.DATA
        s.net_send.msg.payload = s.write_data.wdata

  def line_trace( s ):
    return ''
