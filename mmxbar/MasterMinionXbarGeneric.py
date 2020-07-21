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
from pymtl3.stdlib.mem import MemMasterIfcRTL, MemMinionIfcRTL

from .adapters import DstLogicSingleResp, ReqAdapter, RespAdapter
from .msg_types import mk_req_msg, mk_resp_msg
from pymtl3_net.xbar.XbarRTL import XbarRTL

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

    for i in range( num_requesters ):
      s.req_adapter[i].minion      //= s.minion[i]
      s.req_adapter[i].master.req  //= s.req_net.recv[i]
      s.req_adapter[i].master.resp //= s.resp_net.send[i]

    for i in range( num_responders ):
      s.resp_adapter[i].minion.req  //= s.req_net.send[i]
      s.resp_adapter[i].minion.resp //= s.resp_net.recv[i]
      s.resp_adapter[i].master      //= s.master[i]

  def line_trace( s ):
    lines = []
    minions = [f'{adapter.line_trace()}' for adapter in s.req_adapter]
    masters = [f'{adapter.line_trace()}' for adapter in s.resp_adapter]
    for i, trace in enumerate(minions):
      lines.append(f" Adapted Minion#{i}: {trace}")
    for i, trace in enumerate(masters):
      lines.append(f" Adapted Master#{i}: {trace}")
    return '\n'.join(lines)
