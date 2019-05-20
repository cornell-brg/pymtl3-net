#=========================================================================
# packets.py
#=========================================================================
# Packets definition.
# 
# Author : Yanghui Ou
#   Date : May 20, 2019

from pymtl import *
from BitStruct import mk_bit_struct

def mk_ring_pkt( nrouters=4, opaque_nbits=8, nvcs=2, payload_nbits=32 ):

  IdType = mk_bits( clog2( nrouters ) )
  OpqType = mk_bits( opaque_nbits )
  PayloadType = mk_bits( payload_nbits )
  new_name = "RingPacket_{}_{}_{}_{}".format( 
    nrouters, 
    opaque_nbits,
    nvcs,
    payload_nbits, 
  )
  if nvcs > 1:
    VCIdType = mk_bits( clog2( nvcs ) )
    new_class = mk_bit_struct( new_name,[
      ( 'src',     IdType      ),
      ( 'dst',     IdType      ),
      ( 'opaque',  OpqType     ),
      ( 'vc_id',   VCIdType    ),
      ( 'payload', PayloadType ),
    ])
  else:
    new_class = mk_bit_struct( new_name,[
      ( 'src',     IdType      ),
      ( 'dst',     IdType      ),
      ( 'opaque',  OpqType     ),
      ( 'payload', PayloadType ),
    ])
  return new_class