#=========================================================================
# RouteUnitDORRTL_test.py
#=========================================================================
# Test for RouteUnitDORRTL
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 2, 2019

import tempfile
from pymtl                import *
from ocn_pclib.TestVectorSimulator            import TestVectorSimulator
from router.RouteUnitDORRTL  import RouteUnitDORRTL
from router.Packet import Packet

# class Packet( RTLComponent ):
#  src_x   = Bits(5) 
#  src_y   = 5
#  dst_x   = Bits(5) 
#  dst_y   = 5
#  opaque  = 5 
#  payload = 5

#  def construct( self, src_x, src_y, dst_x, dst_y, opaque, payload ):
#    self.src_x   = src_x
#    self.src_y   = src_y
#    self.dst_x   = dst_x
#    self.dst_y   = dst_y
#    self.opaque  = opaque
#    self.payload = payload  

#  def set( self, src_x, src_y, dst_x, dst_y, opaque, payload ):
#    self.src_x   = src_x
#    self.src_y   = src_y
#    self.dst_x   = dst_x
#    self.dst_y   = dst_y
#    self.opaque  = opaque
#    self.payload = payload  

def run_test( model, test_vectors ):
 
#  model.elaborate()

  def tv_in( model, test_vector ):
    pkt = mk_pkt( test_vector[0], test_vector[1], test_vector[2], test_vector[3],
            test_vector[4], test_vector[5])
    model.recv.msg = pkt
    model.recv.rdy = 1
    model.recv.en  = 1
    for i in range( model.num_outports ):
      model.send[i].rdy = 1

  def tv_out( model, test_vector ):
    assert 1 == 1
  
  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  sim.run_test()

def mk_pkt( src_x, src_y, dst_x, dst_y, opaque, payload ):
  pkt = Packet( src_x, src_y, dst_x, dst_y, opaque, payload )
  pkt.set( src_x, src_y, dst_x, dst_y, opaque, payload )
#  pkt.src_x   = src_x
#  pkt.src_y   = src_y
#  pkt.dst_x   = dst_x
#  pkt.dst_y   = dst_y
#  pkt.opaque  = opaque
#  pkt.payload = payload
  return pkt

def test_RouteUnit( dump_vcd, test_verilog ):
  dimension = 'y'
  pos_x = 1
  pos_y = 1
  model = RouteUnitDORRTL( dimension, 5, pos_x, pos_y)

  run_test( model, [
    #  src_x  src_y  dst_x  dst_y  opaque  payload  
   [     1,     1,     1,     1,     1,    0xdeadd00d  ],
   [     0,     0,     2,     2,     1,    0xdeadcafe  ],
   [     0,     0,     2,     1,     1,    0xdead0afe  ],
   [     0,     0,     1,     2,     1,    0x00000afe  ],
  ])
