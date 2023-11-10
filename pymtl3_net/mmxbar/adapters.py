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
from pymtl3.stdlib.reqresp.ifcs import RequesterIfc, ResponderIfc
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

    s.minion = ResponderIfc( Req,    Resp    )
    s.master = RequesterIfc( NetReq, NetResp )

    # Opaque table

    s.opq_table = Table( OpaqueT, max_req_in_flight )
    s.opq_table.alloc.en    //= lambda: s.minion.reqstream.val & s.minion.reqstream.rdy
    s.opq_table.alloc.msg   //= s.minion.reqstream.msg.opaque
    s.opq_table.dealloc.en  //= lambda: s.minion.respstream.val & s.minion.respstream.rdy
    s.opq_table.dealloc.msg //= s.master.respstream.msg.payload.opaque[ sl_idx ]

    # Destination logic

    s.dst_logic = DstLogicT( Req, SrcT, DstT )
    s.dst_logic.in_req    //= s.minion.reqstream.msg
    s.dst_logic.in_src_id //= id

    # Logic

    s.minion.reqstream.rdy  //= lambda: s.opq_table.alloc.rdy & s.master.reqstream.rdy
    s.minion.respstream.val //= lambda: s.master.respstream.val & s.opq_table.dealloc.rdy

    s.master.reqstream.val  //= lambda: s.minion.reqstream.val & s.opq_table.alloc.rdy
    s.master.respstream.rdy //= s.minion.respstream.rdy

    @update
    def up_master_req_msg():
      s.master.reqstream.msg.dst @= s.dst_logic.out_dst
      s.master.reqstream.msg.payload @= s.minion.reqstream.msg
      s.master.reqstream.msg.payload.opaque[ sl_src ] @= id
      s.master.reqstream.msg.payload.opaque[ sl_idx ] @= s.opq_table.alloc.ret

    @update
    def up_minion_resp_msg():
      s.minion.respstream.msg @= s.master.respstream.msg.payload
      s.minion.respstream.msg.opaque @= s.opq_table.dealloc.ret

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

    s.minion = ResponderIfc( NetReq, NetResp )
    s.master = RequesterIfc( Req,    Resp    )

    # Logic

    s.minion.reqstream.rdy  //= s.master.reqstream.rdy
    s.minion.respstream.val //= s.master.respstream.val

    s.master.reqstream.val  //= s.minion.reqstream.val
    s.master.respstream.rdy //= s.minion.respstream.rdy

    @update
    def up_master_req_msg():
      s.master.reqstream.msg @= s.minion.reqstream.msg.payload

    @update
    def up_minion_resp_msg():
      s.minion.respstream.msg.dst @= s.master.respstream.msg.opaque[ sl_src ]
      s.minion.respstream.msg.payload @= s.master.respstream.msg

  def line_trace( s ):
    return f'{s.minion}({s.id}){s.master}'
