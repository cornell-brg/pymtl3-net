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

#=========================================================================
# cmesh packet
#=========================================================================

def mk_cmesh_pkt( mesh_wid=2, mesh_ht=2, 
                  inports=8, outports=8, nvcs=1, 
                  opaque_nbits=8, payload_nbits=32 ):

  XType = mk_bits( clog2( mesh_wid ) )
  YType = mk_bits( clog2( mesh_ht  ) )
  TType = mk_bits( clog2( outports - 4 ) )
  OpqType = mk_bits( opaque_nbits )
  PayloadType = mk_bits( payload_nbits )
  new_name = "CMeshPacket_{}x{}_{}x{}_{}_{}_{}".format( 
    mesh_wid, 
    mesh_ht,
    inports,
    outports,
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
      ( 'dst_ter', TType       ),
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
      ( 'dst_ter', TType       ),
      ( 'opaque',  OpqType     ),
      ( 'payload', PayloadType ),
    ])
  return new_class


#=========================================================================
# Butterfly packet
#=========================================================================

def mk_bfly_pkt( k_ary=2, n_fly=2, nvcs=0, opaque_nbits=8, payload_nbits=32 ):

  IdType   = mk_bits( clog2( k_ary ** n_fly ) )
  if k_ary == 1:
    KaryType = Bits1
  else:
    KaryType = mk_bits( clog2( k_ary ) )
  if n_fly == 1:
    NflyType = Bits1
  else:
    NflyType = mk_bits( clog2( n_fly ) )
  if k_ary ** ( n_fly - 1 ) == 1:
    RrowType = Bits1
  else:
    RrowType = mk_bits( clog2( k_ary ** ( n_fly - 1 ) ) )
  if k_ary ** ( n_fly - 1 ) == 1:
    DstType = mk_bits( n_fly )
  else:
    DstType = mk_bits( clog2( k_ary ** ( n_fly - 1 ) ) * n_fly )
  OpqType = mk_bits( opaque_nbits )
  PayloadType = mk_bits( payload_nbits )
  new_name = "BflyPacket_{}_{}_{}_{}_{}".format( 
    k_ary,
    n_fly,
    nvcs,
    opaque_nbits,
    payload_nbits, 
  )
  if nvcs > 1:
    VcIdType = mk_bits( clog2( nvcs ) )
    new_class = mk_bit_struct( new_name,[
      ( 'src',     IdType      ),
      ( 'dst',     DstType      ),
      ( 'opaque',  OpqType     ),
      ( 'vc_id',   VcIdType    ),
      ( 'payload', PayloadType ),
    ])
  else:
    new_class = mk_bit_struct( new_name,[
      ( 'src',     IdType      ),
      ( 'dst',     DstType      ),
      ( 'opaque',  OpqType     ),
      ( 'payload', PayloadType ),
    ])
  return new_class

#=========================================================================
# mesh packet with timestamp
#=========================================================================

def mk_mesh_pkt_timestamp( mesh_wid=2, mesh_ht=2, nvcs=1, 
                 opaque_nbits=8, payload_nbits=32, max_time=10 ):

  XType = mk_bits( clog2( mesh_wid ) )
  YType = mk_bits( clog2( mesh_ht  ) )
  OpqType = mk_bits( opaque_nbits )
  PayloadType = mk_bits( payload_nbits )
  TimestampType = mk_bits( clog2(max_time + 1) )
  new_name = "MeshPacketTimestamp_{}x{}_{}_{}_{}".format( 
    mesh_wid, 
    mesh_ht, 
    nvcs, 
    opaque_nbits, 
    payload_nbits,
    max_time
  )

  if nvcs > 1:
    VcIdType = mk_bits( clog2( nvcs ) )
    new_class = mk_bit_struct( new_name,[
      ( 'src_x',     XType         ),
      ( 'src_y',     YType         ),
      ( 'dst_x',     XType         ),
      ( 'dst_y',     YType         ),
      ( 'vc_id',     VcIdType      ),
      ( 'opaque',    OpqType       ),
      ( 'payload',   PayloadType   ),
      ( 'timestamp', TimestampType ),
    ])
  else:
    new_class = mk_bit_struct( new_name,[
      ( 'src_x',     XType         ),
      ( 'src_y',     YType         ),
      ( 'dst_x',     XType         ),
      ( 'dst_y',     YType         ),
      ( 'opaque',    OpqType       ),
      ( 'payload',   PayloadType   ),
      ( 'timestamp', TimestampType ),
    ])
  return new_class

#=========================================================================
# cmesh packet with timestamp
#=========================================================================

def mk_cmesh_pkt_timestamp( mesh_wid=2, mesh_ht=2, inports=8, outports=8, 
    nvcs=1, opaque_nbits=8, payload_nbits=32, max_time=10 ):

  XType = mk_bits( clog2( mesh_wid ) )
  YType = mk_bits( clog2( mesh_ht  ) )
  TType = mk_bits( clog2( outports-4 ) )
  OpqType = mk_bits( opaque_nbits )
  PayloadType = mk_bits( payload_nbits )
  TimestampType = mk_bits( clog2(max_time + 1) )
  new_name = "MeshPacketTimestamp_{}x{}_{}x{}_{}_{}_{}".format( 
    mesh_wid,
    mesh_ht,
    inports,
    outports,
    nvcs, 
    opaque_nbits, 
    payload_nbits,
    max_time
  )

  if nvcs > 1:
    VcIdType = mk_bits( clog2( nvcs ) )
    new_class = mk_bit_struct( new_name,[
      ( 'src_x',     XType         ),
      ( 'src_y',     YType         ),
      ( 'dst_x',     XType         ),
      ( 'dst_y',     YType         ),
      ( 'dst_ter',   TType       ),
      ( 'vc_id',     VcIdType      ),
      ( 'opaque',    OpqType       ),
      ( 'payload',   PayloadType   ),
      ( 'timestamp', TimestampType ),
    ])
  else:
    new_class = mk_bit_struct( new_name,[
      ( 'src_x',     XType         ),
      ( 'src_y',     YType         ),
      ( 'dst_x',     XType         ),
      ( 'dst_y',     YType         ),
      ( 'dst_ter',   TType       ),
      ( 'opaque',    OpqType       ),
      ( 'payload',   PayloadType   ),
      ( 'timestamp', TimestampType ),
    ])
  return new_class


