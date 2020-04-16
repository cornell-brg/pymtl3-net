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
from pymtl3.stdlib.ifcs.mem_ifcs import MemMasterIfcRTL, MemMinionIfcRTL
from ocnlib.utils.commons import has_type, get_field_type

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
    assert has_type( Req,  'opaque' )
    assert has_type( Resp, 'opaque' )

    src_nbits = 1 if num_requesters==1 else clog2( num_requesters )
    dst_nbits = 1 if num_responders==1 else clog2( num_responders )
    idx_nbits = 1 if max_req_in_flight==1 else clog2( max_req_in_flight )
    OpaqueT = get_field_type( Req, 'opaque' )
    SrcT    = mk_bits( src_nbits )
    DstT    = mk_bits( dst_nbits )
    IdxT    = mk_bits( idx_nbits )

    assert src_nbits + idx_nbits <= OpaqueT.nbits, \
      f'opaque field of {Req.__qualname__} has only {opaque.nbits} bits ' \
      f'but {src_nbits} bits is needed for src id and {idx_nbits} for ROB index!'

    sl_src = slice( 0, src_nbits )
    sl_idx = slice( src_nbits, src_nbits+idx_nbits )

    NetReq  = mk_req_msg ( Req, num_responders  )
    NetResp = mk_resp_msg( Resp, num_requesters )

    # Interface

    s.minion = MemMinionIfcRTL( Req,    Resp    )
    s.master = MemMasterIfcRTL( NetReq, NetResp )

    # Opaque table

    s.table = Table( OpaqueT, max_req_in_flight )
    s.table.alloc.en    //= s.minion.req.en
    s.table.alloc.msg   //= s.minion.req.msg.opaque
    s.table.dealloc.en  //= s.master.resp.en
    s.table.dealloc.msg //= s.master.resp.msg.opaque[ sl_idx ]

    # Destination logic

    s.dst_logic = DstLogicT( Req, SrcT, DstT )
    s.dst_logic.in_req    //= s.minion.req
    s.dst_logic.in_src_id //= SrcT(id)

    # Logic

    s.minion.req.rdy //= lambda s.table.alloc.rdy & s.master.req.rdy
    s.minion.resp.en //= lambda s.master.resp.en

    s.master.req.en   //= lambda s.minion.req.en
    s.master.resp.rdy //= lambda s.minion.resp.rdy

    @s.update
    def up_master_req():
      s.master.req.dst = s.dst_logic.req.dst
      s.master.req.msg.payload = s.minion.req
      s.master.req.msg.payload.opaque[ sl_src ] = SrcT(id)
      s.master.req.msg.payload.opaque[ sl_idx ] = s.table.alloc.ret

    @s.update
    def up_minion_resp():
      s.minion.resp = s.master.resp.payload
      s.minion.resp.msg.opaque = s.table.dealloc.ret

  def line_trace( s ):
    return f'{s.minion}(){s.master}'

