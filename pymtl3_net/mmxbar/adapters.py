'''
==========================================================================
adapters.py
==========================================================================
Adapters for the master minion xbar. The field name of the opaque field is
currently hard-coded to be 'opaque'.

Author : Yanghui Ou
  Date : Apr 11, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import MasterIfcRTL, MinionIfcRTL
from pymtl3_net.ocnlib.utils.commons import has_field, get_field_type

from .msg_types import mk_req_msg, mk_resp_msg
from .Table import Table

#-------------------------------------------------------------------------
# DstLogicSingleResp
#-------------------------------------------------------------------------

class DstLogicSingleResp( Component ):

  def construct( s, Req, SrcT, DstT ):

    s.in_req    = InPort ( Req  )
    s.in_src_id = InPort ( SrcT )
    s.out_dst   = OutPort( DstT )

    s.out_dst //= 0

#-------------------------------------------------------------------------
# ReqAdapter
#-------------------------------------------------------------------------

class ReqAdapter( Component ):

  def construct( s, Req, Resp, id,
                 num_requesters, num_responders, max_req_in_flight=2,
                 DstLogicT=DstLogicSingleResp ):

    # Local parameters

    assert num_requesters > 0
    assert num_responders > 0
    assert has_field( Req,  'opaque' )
    assert has_field( Resp, 'opaque' )

    src_nbits = 1 if num_requesters==1 else clog2( num_requesters )
    dst_nbits = 1 if num_responders==1 else clog2( num_responders )
    idx_nbits = 1 if max_req_in_flight==1 else clog2( max_req_in_flight )
    OpaqueT = get_field_type( Req, 'opaque' )
    SrcT    = mk_bits( src_nbits )
    DstT    = mk_bits( dst_nbits )
    IdxT    = mk_bits( idx_nbits )

    assert src_nbits + idx_nbits <= OpaqueT.nbits, \
      f'opaque field of {Req.__qualname__} has only {OpaqueT.nbits} bits ' \
      f'but {src_nbits} bits is needed for src id and {idx_nbits} for ROB index!'

    sl_src = slice( 0, src_nbits )
    sl_idx = slice( src_nbits, src_nbits+idx_nbits )

    NetReq  = mk_req_msg ( Req,  num_responders )
    NetResp = mk_resp_msg( Resp, num_requesters )

    # Interface

    s.minion = MinionIfcRTL( Req,    Resp    )
    s.master = MasterIfcRTL( NetReq, NetResp )

    # Opaque table

    s.opq_table = Table( OpaqueT, max_req_in_flight )
    s.opq_table.alloc.en    //= lambda: s.minion.req.val & s.minion.req.rdy
    s.opq_table.alloc.msg   //= s.minion.req.msg.opaque
    s.opq_table.dealloc.en  //= lambda: s.minion.resp.val & s.minion.resp.rdy
    s.opq_table.dealloc.msg //= s.master.resp.msg.payload.opaque[ sl_idx ]

    # Destination logic

    s.dst_logic = DstLogicT( Req, SrcT, DstT )
    s.dst_logic.in_req    //= s.minion.req.msg
    s.dst_logic.in_src_id //= id

    # Logic

    s.minion.req.rdy  //= lambda: s.opq_table.alloc.rdy & s.master.req.rdy
    s.minion.resp.val //= lambda: s.master.resp.val & s.opq_table.dealloc.rdy

    s.master.req.val  //= lambda: s.minion.req.val & s.opq_table.alloc.rdy
    s.master.resp.rdy //= s.minion.resp.rdy

    @update
    def up_master_req_msg():
      s.master.req.msg.dst @= s.dst_logic.out_dst
      s.master.req.msg.payload @= s.minion.req.msg
      s.master.req.msg.payload.opaque[ sl_src ] @= id
      s.master.req.msg.payload.opaque[ sl_idx ] @= s.opq_table.alloc.ret

    @update
    def up_minion_resp_msg():
      s.minion.resp.msg @= s.master.resp.msg.payload
      s.minion.resp.msg.opaque @= s.opq_table.dealloc.ret

  def line_trace( s ):
    return f'{s.minion}({s.opq_table.line_trace()}){s.master}'

#-------------------------------------------------------------------------
# RespAdapter
#-------------------------------------------------------------------------

class RespAdapter( Component ):

  def construct( s, Req, Resp, id, num_requesters, num_responders ):

    # Local parameter

    assert num_requesters > 0
    assert num_responders > 0
    assert has_field( Req,  'opaque' )
    assert has_field( Resp, 'opaque' )

    src_nbits = 1 if num_requesters==1 else clog2( num_requesters )
    dst_nbits = 1 if num_responders==1 else clog2( num_responders )
    OpaqueT = get_field_type( Resp, 'opaque' )
    SrcT    = mk_bits( src_nbits )
    DstT    = mk_bits( dst_nbits )

    assert src_nbits <= OpaqueT.nbits, \
      f'opaque field of {Resp.__qualname__} has only {OpaqueT.nbits} bits ' \
      f'but {src_nbits} bits is needed for src id!'

    sl_src = slice( 0, src_nbits )
    s.id = DstT(id)

    NetReq  = mk_req_msg ( Req,  num_responders )
    NetResp = mk_resp_msg( Resp, num_requesters )

    # Interface

    s.minion = MinionIfcRTL( NetReq, NetResp )
    s.master = MasterIfcRTL( Req,    Resp    )

    # Logic

    s.minion.req.rdy  //= s.master.req.rdy
    s.minion.resp.val //= s.master.resp.val

    s.master.req.val  //= s.minion.req.val
    s.master.resp.rdy //= s.minion.resp.rdy

    @update
    def up_master_req_msg():
      s.master.req.msg @= s.minion.req.msg.payload

    @update
    def up_minion_resp_msg():
      s.minion.resp.msg.dst @= s.master.resp.msg.opaque[ sl_src ]
      s.minion.resp.msg.payload @= s.master.resp.msg

  def line_trace( s ):
    return f'{s.minion}({s.id}){s.master}'
