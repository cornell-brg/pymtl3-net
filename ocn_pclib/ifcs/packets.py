#=========================================================================
# packets.py
#=========================================================================
# Packets definition.
# 
# Author : Yanghui Ou
#   Date : May 20, 2019

from pymtl3 import *

#=========================================================================
# ring packet
#=========================================================================

def mk_ring_pkt( nrouters=4, nvcs=2, opaque_nbits=8, payload_nbits=32 ):

  IdType = mk_bits( clog2( nrouters ) )
  OpqType = mk_bits( opaque_nbits )
  PayloadType = mk_bits( payload_nbits )
  new_name = "RingPacket_{}_{}_{}_{}".format( 
    nrouters, 
    nvcs,
    opaque_nbits,
    payload_nbits, 
  )
  if nvcs > 1:
    VcIdType = mk_bits( clog2( nvcs ) )
    new_class = mk_bit_struct( new_name,[
      ( 'src',     IdType      ),
      ( 'dst',     IdType      ),
      ( 'opaque',  OpqType     ),
      ( 'vc_id',   VcIdType    ),
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

#=========================================================================
# mesh packet
#=========================================================================

def mk_mesh_pkt( mesh_wid=2, mesh_ht=2, nvcs=1, 
                 opaque_nbits=8, payload_nbits=32 ):

  XType = mk_bits( clog2( mesh_wid ) )
  YType = mk_bits( clog2( mesh_ht  ) )
  OpqType = mk_bits( opaque_nbits )
  PayloadType = mk_bits( payload_nbits )
  new_name = "MeshPacket_{}x{}_{}_{}_{}".format( 
    mesh_wid, 
    mesh_ht, 
    nvcs, 
    opaque_nbits, 
    payload_nbits
  )

  if nvcs > 1:
    VcIdType = mk_bits( clog2( nvcs ) )
    new_class = mk_bit_struct( new_name,[
      ( 'src_x',   XType       ),
      ( 'src_y',   YType       ),
      ( 'dst_x',   XType       ),
      ( 'dst_y',   YType       ),
      ( 'vc_id',   VcIdType    ),
      ( 'opaque',  OpqType     ),
      ( 'payload', PayloadType ),
    ])
  else:
    new_class = mk_bit_struct( new_name,[
      ( 'src_x',   XType       ),
      ( 'src_y',   YType       ),
      ( 'dst_x',   XType       ),
      ( 'dst_y',   YType       ),
      ( 'opaque',  OpqType     ),
      ( 'payload', PayloadType ),
    ])
  return new_class
