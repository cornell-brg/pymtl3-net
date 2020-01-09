'''
==========================================================================
axi_msgs.py
==========================================================================
Bitstructs for axi interface.
TODO: parametrize bitwidth

Author : Yanghui Ou
  Date : Jan 1, 2020
'''

from pymtl3 import *

#-------------------------------------------------------------------------
# AXI4 format
#-------------------------------------------------------------------------

BitsNOCDataWidth = Bits64
BitsAXI4IDWidth  = Bits6
BitsAXI4AddrWidth = Bits64
BitsAXI4LenWidth = Bits8
BitsAXI4SizeWidth = Bits3
BitsAXI4BurstWidth = Bits2
BitsAXI4CacheWidth = Bits4
BitsAXI4PortWidth = Bits3
BitsAXI4QoSWidth = Bits4
BitsAXI4RegionWidth = Bits4
BitsAXI4UserWidth = Bits11
BitsAXI4DataWidth = Bits512
BitsAXI4RespWidth = Bits2
BitsAXI4StrbWidth = Bits64

@bitstruct
class AXI4AddrRead:
  arid     : Bits6
  araddr   : BitsAXI4AddrWidth # Bits64
  arlen    : Bits8
  arsize   : Bits3
  arburst  : Bits2
  arlock   : Bits1
  arcache  : Bits4
  arprot   : Bits3
  arqos    : Bits4
  arregion : Bits4
  aruser   : Bits11

  def __str__( self ):
    return f'{self.araddr}'

@bitstruct
class AXI4DataRead:
  rid   : Bits6
  rdata : BitsAXI4DataWidth # Bits512
  rresp : Bits2
  rlast : Bits1
  ruser : Bits11

  def __str__( self ):
    return f'{self.rdata[480:512]}...{self.rdata[0:32]}'

@bitstruct
class AXI4AddrWrite:
  awid     : Bits6
  awaddr   : BitsAXI4AddrWidth # Bits64
  awlen    : Bits8
  awsize   : Bits3
  awburst  : Bits2
  awlock   : Bits1
  awcache  : Bits4
  awprot   : Bits3
  awqos    : Bits4
  awregion : Bits4
  awuser   : Bits11

  def __str__( self ):
    return f'{self.awaddr}'

@bitstruct
class AXI4DataWrite:
  wid      : Bits6
  wdata    : BitsAXI4DataWidth # Btis512 
  wstrb    : Bits64
  wlast    : Bits1
  wuser    : Bits11

  def __str__( self ):
    return f'{self.wstrb}:{self.wdata[480:512]}...{self.wdata[0:32]}'

@bitstruct
class AXI4WriteResp:
  bid   : Bits6
  bresp : Bits2
  buser : Bits11

#-------------------------------------------------------------------------
# Network message
#-------------------------------------------------------------------------

# HEADER

USER   = slice(0,  11)
REGION = slice(11, 15)
QOS    = slice(15, 19)
PROT   = slice(19, 22)
CACHE  = slice(22, 26)
LOCK   = slice(26, 27)
BURST  = slice(27, 29)
SIZE   = slice(29, 32)
LEN    = slice(32, 40)
MTYPE  = slice(40, 44)
OPQ    = slice(44, 64)

TYPE_RD = b4(0)
TYPE_WR = b4(1)

