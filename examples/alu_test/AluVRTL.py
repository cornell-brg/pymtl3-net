"""
==========================================================================
AluVRTL.py
==========================================================================
Imported ALU from Verilog.

Author : Cheng Tan
  Date : July 18, 2019
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

class Alu( Placeholder, Component ):

  def construct( s, import_params ):

    # Metadata for import
    s.sverilog_params = import_params
    s.sverilog_import = True
    s.sverilog_import_path = "../Alu.v"

    # Local parameter
    DataType = mk_bits( import_params["width_p"] )

    # Interface
    s.v_i          = InPort( Bits1 )
    s.opd_a_i      = InPort( DataType )
    s.opd_b_i      = InPort( DataType )
    s.alu_op_i     = InPort( Bits3 )
    s.v_o          = OutPort( Bits1 )
    s.res_o        = OutPort( DataType )
    s.branch_res_o = OutPort( Bits1 )

#-------------------------------------------------------------------------
# Wrapper
#-------------------------------------------------------------------------
# A wrapper that has method based interface around the verilog module.

class AluVRTL( Component ):

  def construct( s, ReqType, RespType ):
    s.enq = EnqIfcRTL( ReqType  )
    s.deq = DeqIfcRTL( RespType )
    assert ReqType.data_nbits == RespType.data_nbits

    s.alu = Alu({
      "width_p"  : ReqType.data_nbits,
    })(
      v_i          = s.enq.en,
      opd_a_i      = s.enq.msg.in1,
      opd_b_i      = s.enq.msg.in2,
      alu_op_i     = s.enq.msg.op,
      res_o        = s.deq.msg.result,
      branch_res_o = s.deq.msg.branch,
    )
    
    @s.update
    def set_rdy():
      s.enq.rdy = b1(1) 
      s.deq.rdy = s.alu.v_o

  def line_trace( s ):
    return "{}->{}".format( s.enq, s.deq )
