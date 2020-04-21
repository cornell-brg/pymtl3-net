'''
==========================================================================
MasterMinionXbarGeneric.py
==========================================================================
A generic master-minion crossbar that is parametrized by:
  - type of request message
  - type of response message
  - number of requesters
  - number of responders
  - destination logic (if there are multiple responders)

Author : Yanghui Ou
  Date : Apr 15, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs.mem_ifcs import MemMasterIfcRTL, MemMinionIfcRTL

from .adapters import DstLogicSingleResp, ReqAdapter, RespAdapter
from .msg_types import mk_req_msg, mk_resp_msg
from ..xbar import XbarRTL

class MasterMinionXbarGeneric( Component ):

  def construct( s, Req, Resp, num_requesters, num_responders, max_req_in_flight=2, DstLogicT=DstLogicSingleResp ):

    # Local parameter

    NetReq  = mk_req_msg ( Req,  num_responders )
    NetResp = mk_resp_msg( Resp, num_requesters )

    # Interface

    s.minion = [ MemMinionIfcRTL( Req, Resp ) for _ in range( num_requesters ) ]
    s.master = [ MemMasterIfcRTL( Req, Resp ) for _ in range( num_responders ) ]

    # Component

    s.req_net  = XbarRTL( NetReq,  num_requesters, num_responders )
    s.resp_net = XbarRTL( NetResp, num_responders, num_requesters )

    s.req_adapter  = [ ReqAdapter( Req, Resp, i, num_requesters, num_responders, max_req_in_flight, DstLogicT ) for i in range( num_requesters ) ]
    s.resp_adapter = [ RespAdapter( Req, Resp, i, num_requesters, num_responders ) for i  in range( num_responders ) ]

    # Connections

  def line_trace( s ):
    return f'()'
