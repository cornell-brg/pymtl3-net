'''
==========================================================================
AXI4Slave2NetSend.py
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

class AXI4Slave2NetSend( Component ):

  def construct( s, PktType, xpos=0, ypos=0 ):

    # AXI Slave interface

    s.read_addr = RecvIfcRTL( AXI4AddrRead )
    # s.read_data = SendIfcRTL( AXI4DataRead )

    s.write_addr = RecvIfcRTL( AXI4AddrWrite )
    s.write_data = RecvIfcRTL( AXI4DataWrite )
    # s.write_resp = SendIfcRTL( AXI4WriteResp )

    # Network interface

    s.net_send = SendIfcRTL( PktType )
    # s.net_recv = SendIfcRTL( PktType )

    # Constants

    s.HEADER = b2(0) # Assemble header packet
    s.ADDR   = b2(1) # Assemble addr packet 
    s.DATA   = b2(2) # Assemble body packet

    s.xpos   = b3( xpos )
    s.ypos   = b3( ypos )

    # Registers

    s.state    = Wire( Bits2  )
    s.dst_x_r  = Wire( Bits3  )
    s.dst_y_r  = Wire( Bits3  )

    s.is_rd_r = Wire( Bits1  )
    s.is_wr_r = Wire( Bits1  )
    s.len_r   = Wire( Bits8  )
    s.addr_r  = Wire( Bits64 )

    # Wires

    s.state_next = Wire( Bits2 )

    # Logic

    s.read_addr.rdy  //= lambda: ( s.state == s.HEADER ) & s.net_send.rdy
    s.write_addr.rdy //= lambda: ( s.state == s.HEADER ) & s.net_send.rdy
    s.write_data.rdy //= lambda: ( s.state == s.DATA   ) & s.net_send.rdy
    s.net_send.en    //= lambda: s.read_addr.en | s.write_addr.en | s.write_data.en | ( s.state == s.ADDR ) & s.net_send.rdy

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
        if s.net_send.en & s.is_wr_r:
          s.state_next = s.DATA
        elif s.net_send.en & s.is_rd_r:
          s.state_next = s.HEADER
        else:
          s.state_next = s.ADDR

      else: # s.state == s.DATA
        if ( s.len_r == b8(1) ) & s.net_send.en:
          s.state_next = s.HEADER
        else:
          s.state_next = s.DATA

    s.net_send.msg.src_x //= s.xpos
    s.net_send.msg.src_y //= s.ypos

    @s.update
    def up_dst_pos():
      if ( s.state == s.HEADER ) & s.read_addr.en:
        s.net_send.msg.dst_x = s.read_addr.msg.arid[3:6]
        s.net_send.msg.dst_y = s.read_addr.msg.arid[0:3]

      elif ( s.state == s.HEADER ) & s.write_addr.en:
        s.net_send.msg.dst_x = s.write_addr.msg.awid[3:6]
        s.net_send.msg.dst_y = s.write_addr.msg.awid[0:3]
      
      else:
        s.net_send.msg.dst_x = s.dst_x_r
        s.net_send.msg.dst_y = s.dst_y_r

    @s.update_ff
    def up_len_r():
      if ( s.state == s.HEADER ) & s.read_addr.en:
        s.len_r <<= s.read_addr.msg.arlen
      elif ( s.state == s.HEADER ) & s.write_addr.en:
        s.len_r <<= s.write_addr.msg.awlen
      elif ( s.state == s.DATA ) & s.net_send.en:
        s.len_r <<= s.len_r - b8(1)
      else:
        s.len_r <<= s.len_r

    @s.update_ff
    def up_misc_reg():
      if ( s.state == s.HEADER ) & s.read_addr.en:
        s.is_rd_r <<= b1(1)
        s.is_wr_r <<= b1(0)
        s.addr_r  <<= s.read_addr.msg.araddr
      elif ( s.state == s.HEADER ) & s.write_addr.en:
        s.is_rd_r <<= b1(0)
        s.is_wr_r <<= b1(1)
        s.addr_r  <<= s.write_addr.msg.awaddr
      else:
        s.is_rd_r <<= s.is_rd_r
        s.is_wr_r <<= s.is_wr_r
        s.addr_r  <<= s.addr_r

    @s.update
    def up_payload():
      if s.state == s.HEADER:

        # Assembles a read request
        if s.read_addr.en:
          s.net_send.msg.opaque            = TYPE_RD
          s.net_send.msg.payload[ LEN    ] = s.read_addr.msg.arlen
          s.net_send.msg.payload[ SIZE   ] = s.read_addr.msg.arsize
          s.net_send.msg.payload[ BURST  ] = s.read_addr.msg.arburst
          s.net_send.msg.payload[ LOCK   ] = s.read_addr.msg.arlock
          s.net_send.msg.payload[ CACHE  ] = s.read_addr.msg.arcache
          s.net_send.msg.payload[ PROT   ] = s.read_addr.msg.arprot
          s.net_send.msg.payload[ QOS    ] = s.read_addr.msg.arqos
          s.net_send.msg.payload[ REGION ] = s.read_addr.msg.arregion
          s.net_send.msg.payload[ USER   ] = s.read_addr.msg.aruser

        # Assembles a write request
        elif s.write_addr.en:
          s.net_send.msg.opaque            = TYPE_WR
          s.net_send.msg.payload[ LEN    ] = s.write_addr.msg.awlen
          s.net_send.msg.payload[ SIZE   ] = s.write_addr.msg.awsize
          s.net_send.msg.payload[ BURST  ] = s.write_addr.msg.awburst
          s.net_send.msg.payload[ LOCK   ] = s.write_addr.msg.awlock
          s.net_send.msg.payload[ CACHE  ] = s.write_addr.msg.awcache
          s.net_send.msg.payload[ PROT   ] = s.write_addr.msg.awprot
          s.net_send.msg.payload[ QOS    ] = s.write_addr.msg.awqos
          s.net_send.msg.payload[ REGION ] = s.write_addr.msg.awregion
          s.net_send.msg.payload[ USER   ] = s.write_addr.msg.awuser

        else:
          s.net_send.msg.payload = b64(0)
          
      elif s.state == s.ADDR:
        s.net_send.msg.payload = s.addr_r

      else: # s.state == s.DATA
        s.net_send.msg.payload = s.write_data.msg.wdata

  def line_trace( s ):
    return f'{s.read_addr}II{s.write_addr}|{s.write_data}({s.state}){s.net_send}'
