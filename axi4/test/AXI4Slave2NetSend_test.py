'''
==========================================================================
AXI4Slave2NetSend_test.py
==========================================================================
Unit tests for AXI4Slave2NetSend.

Author : Yanghui Ou
  Date : Jan 9, 2020
'''

from pymtl3 import *
from ocn_pclib.ifcs.packets import mk_mesh_pkt
from ..AXI4Slave2NetSend import AXI4Slave2NetSend
from ..axi4_msgs import *

#-------------------------------------------------------------------------
# sanity check
#-------------------------------------------------------------------------

def test_sanity_check():
  PktType = mk_mesh_pkt( ncols=8, nrows=8, payload_nbits=64 ) 
  dut = AXI4Slave2NetSend( PktType )
  dut.elaborate()
  dut.apply( SimulationPass() )
  dut.sim_reset()
  dut.tick()
  dut.tick()
  dut.tick()

#-------------------------------------------------------------------------
# adhoc write test
#-------------------------------------------------------------------------

def test_adhoc_write():
  print()
  PktType = mk_mesh_pkt( ncols=8, nrows=8, payload_nbits=64 ) 
  dut = AXI4Slave2NetSend( PktType )
  dut.elaborate()
  dut.apply( SimulationPass() )
  dut.sim_reset()

  dut.net_send.rdy = b1(1)
  dut.eval_combinational()
  print( dut.line_trace() )
  dut.tick()

  assert dut.write_addr.rdy
  dut.write_addr.msg = AXI4AddrWrite( awid=0b111_011, awaddr=0xdeadface, awlen=4 )
  dut.write_addr.en  = b1(1)
  dut.eval_combinational()
  print( dut.line_trace() )
  dut.tick()
  dut.write_addr.en  = b1(0)
  
  assert ~dut.write_data.rdy
  dut.eval_combinational()
  print( dut.line_trace() )
  dut.tick()

  # assert dut.write_data.rdy
  dut.write_data.msg = AXI4DataWrite( wstrb=0xff, wdata=0xfeedbeef )
  dut.write_data.en  = b1(1)
  dut.eval_combinational()
  print( dut.line_trace() )
  dut.tick()
  dut.write_data.en  = b1(0)

  assert dut.write_data.rdy
  dut.write_data.msg = AXI4DataWrite( wstrb=0xff, wdata=0xcafebabe )
  dut.write_data.en  = b1(1)
  dut.eval_combinational()
  print( dut.line_trace() )
  dut.tick()
  dut.write_data.en  = b1(0)

  assert dut.write_data.rdy
  dut.write_data.msg = AXI4DataWrite( wstrb=0xff, wdata=0xfeeddead )
  dut.write_data.en  = b1(1)
  dut.eval_combinational()
  print( dut.line_trace() )
  dut.tick()
  dut.write_data.en  = b1(0)

  assert dut.write_data.rdy
  dut.write_data.msg = AXI4DataWrite( wstrb=0xff, wdata=0xfaceb00c )
  dut.write_data.en  = b1(1)
  dut.eval_combinational()
  print( dut.line_trace() )
  dut.tick()
  dut.write_data.en  = b1(0)

  dut.eval_combinational()
  print( dut.line_trace() )
  dut.tick()

  dut.eval_combinational()
  print( dut.line_trace() )
  dut.tick()

#-------------------------------------------------------------------------
# adhoc read test
#-------------------------------------------------------------------------

def test_adhoc_read():
  print()
  PktType = mk_mesh_pkt( ncols=8, nrows=8, payload_nbits=64 ) 
  dut = AXI4Slave2NetSend( PktType )
  dut.elaborate()
  dut.apply( SimulationPass() )
  dut.sim_reset()

  dut.net_send.rdy = b1(1)
  dut.eval_combinational()
  print( dut.line_trace() )
  dut.tick()

  assert dut.read_addr.rdy
  dut.read_addr.msg = AXI4AddrRead( arid=0b111_011, araddr=0xdeadface, arlen=4 )
  dut.read_addr.en  = b1(1)
  dut.eval_combinational()
  print( dut.line_trace() )
  dut.tick()
  dut.read_addr.en  = b1(0)
  
  dut.eval_combinational()
  print( dut.line_trace() )
  dut.tick()

  dut.eval_combinational()
  print( dut.line_trace() )
  dut.tick()

  dut.eval_combinational()
  print( dut.line_trace() )
  dut.tick()
