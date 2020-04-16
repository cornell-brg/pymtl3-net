'''
==========================================================================
msg_types.py
==========================================================================
Message types for the master-minion xbar.

Author : Yanghui Ou
  Date : Apr 11, 2020
'''
from pymtl3 import *
from pymtl3.datatypes.bitstructs import(
  is_bitstruct_class,
  is_bitstruct_inst,
  _FIELDS as bitstruct_fields,
)

#------------------------------------------------------------------------
# mk_req_msg
#-------------------------------------------------------------------------

def mk_req_msg( ReqType, num_responders ):
  assert num_responders > 0
  dst_nbits = 1 if num_responders == 1 else clog2( num_responders )
  cls_name = f'mmxbar_req_{num_responders}_{ReqType.__name__}'
  return mk_bitstruct( cls_name, {
    'dst'     : mk_bits( dst_nbits ),
    'payload' : ReqType,
  })

#------------------------------------------------------------------------
# mk_resp_msg
#-------------------------------------------------------------------------

def mk_resp_msg( RespType, num_requesters ):
  assert num_responders > 0
  dst_nbits = 1 if num_requesters == 1 else clog2( num_requesters )
  cls_name = f'mmxbar_resp_{num_responders}_{ReqType.__name__}'
  return mk_bitstruct( cls_name, {
    'dst'     : mk_bits( dst_nbits ),
    'payload' : RespType,
  })
