"""
==========================================================================
FifoVRTL.py
==========================================================================
Imported Fifo from Verilog.

Author : Cheng Tan
  Date : July 19, 2019
"""
from __future__ import absolute_import, division, print_function

from pymtl3 import *
from pymtl3.dsl import Placeholder
from pymtl3.passes.sverilog import ImportPass
from pymtl3.stdlib.ifcs import DeqIfcRTL, EnqIfcRTL

#-------------------------------------------------------------------------
# Placeholder
#-------------------------------------------------------------------------
# A placeholder for the imported verilog module.

class Fifo( Placeholder, Component ):

  def construct( s, import_params ):

    # Metadata for import
    s.sverilog_params = import_params
    s.sverilog_import = True
    s.sverilog_import_path = "../bsg_fifo_1r1w_rolly.v"

    # Local parameter
    DataType = mk_bits( import_params["width_p"] )
    ElsType  = mk_bits( import_params["els_p"] )
    ready_THEN_valid_p = import_params["ready_THEN_valid_p"]

    # Interface
    s.clr_v_i  = InPort( Bits1 )
    s.ckpt_v_i = InPort( Bits1 )
    s.roll_v_i = InPort( Bits1 )
    s.data_i   = InPort( DataType )
    s.v_i      = InPort( Bits1 )

    s.ready_o  = OutPort( Bits1 )
    s.data_o   = OutPort( DataType )
    s.v_o      = OutPort( Bits1 )

    s.yumi_i   = InPort( Bits1 )

#-------------------------------------------------------------------------
# Wrapper
#-------------------------------------------------------------------------
# A wrapper that has method based interface around the verilog module.

class FifoVRTL( Component ):

  def construct( s, ReqType, RespType ):
    s.enq = EnqIfcRTL( ReqType  )
    s.deq = DeqIfcRTL( RespType )
    assert ReqType.data_nbits == RespType.data_nbits

    s.fifo = Fifo({
      "width_p"            : ReqType.data_nbits,
      "els_p"              : ReqType.els,
      "ready_THEN_valid_p" : ReqType.ready,
    })(
      clr_v_i  = s.enq.msg.clr,
      ckpt_v_i = s.enq.msg.ckpt,
      roll_v_i = s.enq.msg.roll,
      data_i   = s.enq.msg.data,
      v_i      = s.enq.en,

      data_o   = s.deq.msg.data,

      yumi_i   = s.enq.msg.yumi
    )
    
    @s.update
    def set_rdy():
      s.enq.rdy = b1(1) 
      s.deq.rdy = s.fifo.v_o

  def line_trace( s ):
    return "{}->{}".format( s.enq, s.deq )
