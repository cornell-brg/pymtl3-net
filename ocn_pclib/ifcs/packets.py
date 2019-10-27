"""
==========================================================================
packets.py
==========================================================================
Collection of packets definition.

Convention: The fields/constructor arguments should appear in the order
            of [ <id related>, opaque_nbits, vc, payload_nbits ]

Author : Yanghui Ou, Shunning Jiang
  Date : Oct 26, 2019
"""
from pymtl3 import *

#=========================================================================
# Generic packet
#=========================================================================

def mk_generic_pkt( nrouters=4, opaque_nbits=8, vc=2, payload_nbits=16,
                    prefix="GenericPacket" ):

  IdType = mk_bits( clog2( nrouters ) )
  OpqType = mk_bits( opaque_nbits )
  PayloadType = mk_bits( payload_nbits )

  new_name = f"{prefix}_{nrouters}_{vc}_{opaque_nbits}_{payload_nbits}"

  if vc > 1:
    VcIdType = mk_bits( clog2( vc ) )

    def str_func( s ):
      return f"{s.src}>{s.dst}:{s.opaque}:{s.vc_id}:{s.payload}"

    return mk_bitstruct( new_name, {
        'src':     IdType,
        'dst':     IdType,
        'opaque':  OpqType,
        'vc_id':   VcIdType,
        'payload': PayloadType,
      },
      namespace = { '__str__': str_func }
    )

  else:
    def str_func( s ):
      return f"{s.src}>{s.dst}:{s.opaque}:{s.payload}"

    return mk_bitstruct( new_name, {
        'src':     IdType,
        'dst':     IdType,
        'opaque':  OpqType,
        'payload': PayloadType,
      },
      namespace = { '__str__': str_func }
    )

#=========================================================================
# ring packet
#=========================================================================

def mk_ring_pkt( nrouters=4, opaque_nbits=8, vc=2, payload_nbits=32 ):
  return mk_generic_pkt( nrouters, opaque_nbits, vc, payload_nbits, "RingPacket" )

#=========================================================================
# mesh packet
#=========================================================================

def mk_mesh_pkt( mesh_width=2, mesh_height=2,
                 opaque_nbits=8, vc=1, payload_nbits=32 ):
  assert mesh_width > 0 and mesh_height > 0

  XType       = mk_bits(clog2( mesh_width )) if mesh_width != 1 else Bits1
  YType       = mk_bits(clog2( mesh_height)) if mesh_height!= 1 else Bits1
  OpqType     = mk_bits(opaque_nbits)
  PayloadType = mk_bits(payload_nbits)

  new_name = f"MeshPacket_{mesh_width}x{mesh_height}_{vc}_{opaque_nbits}_{payload_nbits}"

  if vc > 1:
    VcIdType = mk_bits( clog2( vc ) )

    def str_func( s ):
      return f"({s.src_x},{s.src_y})>({s.dst_x},{s.dst_y}):{s.opaque}:{s.vc_id}:{s.payload}"

    return mk_bitstruct( new_name, {
        'src_x':   XType,
        'src_y':   YType,
        'dst_x':   XType,
        'dst_y':   YType,
        'opaque':  OpqType,
        'vc_id':   VcIdType,
        'payload': PayloadType,
      },
      namespace = { '__str__': str_func },
    )
  else:
    def str_func( s ):
      return f"({s.src_x},{s.src_y})>({s.dst_x},{s.dst_y}):{s.opaque}:{s.payload}"

    return mk_bitstruct( new_name, {
        'src_x':   XType,
        'src_y':   YType,
        'dst_x':   XType,
        'dst_y':   YType,
        'opaque':  OpqType,
        'payload': PayloadType,
      },
      namespace = { '__str__': str_func }
    )

#=========================================================================
# cmesh packet
#=========================================================================

def mk_cmesh_pkt( mesh_width=2, mesh_height=2,
                  inports=8, outports=8,
                  opaque_nbits=8, vc=1, payload_nbits=32 ):

  XType = mk_bits(clog2(mesh_width))  if mesh_width  != 1 else Bits1
  YType = mk_bits(clog2(mesh_height)) if mesh_height != 1 else Bits1
  TType = mk_bits(clog2(outports-4))  if outports > 5 else Bits1
  OpqType = mk_bits( opaque_nbits )
  PayloadType = mk_bits( payload_nbits )

  new_name = f"CMeshPacket_{mesh_width}x{mesh_height}_{inports}x{outports}_" \
             f"{opaque_nbits}_{vc}_{payload_nbits}"

  if vc > 1:
    VcIdType = mk_bits( clog2( vc ) )
    return mk_bitstruct( new_name, {
      'src_x':   XType,
      'src_y':   YType,
      'dst_x':   XType,
      'dst_y':   YType,
      'dst_ter': TType,
      'opaque':  OpqType,
      'vc_id':   VcIdType,
      'payload': PayloadType,
    })
  else:
    return mk_bitstruct( new_name, {
      'src_x':   XType,
      'src_y':   YType,
      'dst_x':   XType,
      'dst_y':   YType,
      'dst_ter': TType,
      'opaque':  OpqType,
      'payload': PayloadType,
    })

#=========================================================================
# Butterfly packet
#=========================================================================

def mk_bfly_pkt( k_ary=2, n_fly=2, opaque_nbits=8, vc=0, payload_nbits=32 ):
  IdType   = mk_bits( clog2( k_ary ** n_fly ) )

  # if k_ary == 1:
  #   KaryType = Bits1
  # else:
  #   KaryType = mk_bits( clog2( k_ary ) )
  # if n_fly == 1:
  #   NflyType = Bits1
  # else:
  #   NflyType = mk_bits( clog2( n_fly ) )
  # if k_ary ** ( n_fly - 1 ) == 1:
  #   RrowType = Bits1
  # else:
  #   RrowType = mk_bits( clog2( k_ary ** ( n_fly - 1 ) ) )

  if k_ary ** ( n_fly - 1 ) == 1:
    DstType = mk_bits( n_fly )
  else:
    DstType = mk_bits( clog2( k_ary ) * n_fly )
    # DstType  = mk_bits( clog2( k_ary ** ( n_fly - 1 ) ) * n_fly )

  OpqType = mk_bits( opaque_nbits )
  PayloadType = mk_bits( payload_nbits )

  new_name = f"BflyPacket_{k_ary}_{n_fly}_{vc}_{opaque_nbits}_{payload_nbits}"

  if vc > 1:
    VcIdType = mk_bits( clog2(vc) )

    return mk_bitstruct( new_name, {
      'src':     IdType,
      'dst':     DstType,
      'opaque':  OpqType,
      'vc_id':   VcIdType,
      'payload': PayloadType,
    })
  else:
    return mk_bitstruct( new_name, {
      'src':     IdType,
      'dst':     DstType,
      'opaque':  OpqType,
      'payload': PayloadType,
    })

#=========================================================================
# ring packet with timestamp
#=========================================================================

def mk_ring_pkt_timestamp( nrouters=4, opaque_nbits=8, vc=2, payload_nbits=32, max_time=10 ):

  IdType = mk_bits( clog2( nrouters ) )
  OpqType = mk_bits( opaque_nbits )
  PayloadType = mk_bits( payload_nbits )
  TimestampType = mk_bits( clog2(max_time + 1) )
  new_name = f"RingPacketTimestamp_{nrouters}_{opaque_nbits}_{vc}_{payload_nbits}_{max_time}"

  if vc > 1:
    VcIdType = mk_bits( clog2( vc ) )

    def str_func( s ):
      return f"{s.src}>{s.dst}:{s.opaque}:{s.vc_id}:{s.payload}:{s.timestamp}"

    return mk_bitstruct( new_name, {
        'src':       IdType,
        'dst':       IdType,
        'opaque':    OpqType,
        'vc_id':     VcIdType,
        'payload':   PayloadType,
      },
      namespace = { '__str__': str_func }
    )
  else:
    def str_func( s ):
      return f"{s.src}>{s.dst}:{s.opaque}:{s.payload}:{s.timestamp}"

    return mk_bitstruct( new_name, {
        'src':       IdType,
        'dst':       IdType,
        'opaque':    OpqType,
        'payload':   PayloadType,
        'timestamp': TimestampType,
      },
      namespace = { '__str__': str_func }
    )

#=========================================================================
# mesh packet with timestamp
#=========================================================================

def mk_mesh_pkt_timestamp( mesh_width=2, mesh_height=2,
                           opaque_nbits=8, vc=1, payload_nbits=32,
                           max_time=10 ):

  XType = mk_bits( clog2( mesh_width ) )
  YType = mk_bits( clog2( mesh_height  ) )
  OpqType = mk_bits( opaque_nbits )
  PayloadType = mk_bits( payload_nbits )
  TimestampType = mk_bits( clog2(max_time + 1) )
  new_name = f"MeshPacketTimestamp_{mesh_width}x{mesh_height}_{opaque_nbits}"\
             f"_{vc}_{payload_nbits}_{max_time}"

  if vc > 1:
    VcIdType = mk_bits( clog2( vc ) )

    def str_func( s ):
      return f"({s.src_x},{s.src_y})>({s.dst_x},{s.dst_y}):{s.opaque}:{s.vc_id}:{s.payload}"

    return mk_bitstruct( new_name, {
        'src_x':   XType,
        'src_y':   YType,
        'dst_x':   XType,
        'dst_y':   YType,
        'opaque':  OpqType,
        'vc_id':   VcIdType,
        'payload': PayloadType,
      },
      namespace = { '__str__': str_func },
    )
  else:
    def str_func( s ):
      return f"({s.src_x},{s.src_y})>({s.dst_x},{s.dst_y}):{s.opaque}:{s.payload}"

    return mk_bitstruct( new_name, {
        'src_x':   XType,
        'src_y':   YType,
        'dst_x':   XType,
        'dst_y':   YType,
        'opaque':  OpqType,
        'payload': PayloadType,
      },
      namespace = { '__str__': str_func }
    )

  if vc > 1:
    VcIdType = mk_bits( clog2( vc ) )

    def str_func( s ):
      return f"({s.src_x},{s.src_y})>({s.dst_x},{s.dst_y}):{s.opaque}:{s.vc_id}:{s.payload}:{s.timestamp}"

    return mk_bitstruct( new_name, {
        'src_x':     XType,
        'src_y':     YType,
        'dst_x':     XType,
        'dst_y':     YType,
        'opaque':    OpqType,
        'vc_id':     VcIdType,
        'payload':   PayloadType,
        'timestamp': TimestampType,
      },
      namespace = { '__str__': str_func },
    )

  else:
    def str_func( s ):
      return f"({s.src_x},{s.src_y})>({s.dst_x},{s.dst_y}):{s.opaque}:{s.payload}:{s.timestamp}"

    return mk_bitstruct( new_name, {
        'src_x':     XType,
        'src_y':     YType,
        'dst_x':     XType,
        'dst_y':     YType,
        'opaque':    OpqType,
        'payload':   PayloadType,
        'timestamp': TimestampType,
      },
      namespace = { '__str__': str_func },
    )

#=========================================================================
# cmesh packet with timestamp
#=========================================================================

def mk_cmesh_pkt_timestamp( mesh_width=2, mesh_height=2, inports=8, outports=8,
    opaque_nbits=8, vc=1, payload_nbits=32, max_time=10 ):

  XType = mk_bits( clog2( mesh_width ) )
  YType = mk_bits( clog2( mesh_height  ) )
  TType = mk_bits(clog2( outports - 4 )) if outports > 5 else mk_bits(1)
  OpqType = mk_bits( opaque_nbits )
  PayloadType = mk_bits( payload_nbits )
  TimestampType = mk_bits( clog2(max_time + 1) )
  new_name = f"MeshPacketTimestamp_{mesh_width}x{mesh_height}_{inports}x{outports}"\
             f"_{vc}_{opaque_nbits}_{payload_nbits}_{max_time}"

  if vc > 1:
    VcIdType = mk_bits( clog2( vc ) )
    return mk_bitstruct( new_name, {
      'src_x':     XType,
      'src_y':     YType,
      'dst_x':     XType,
      'dst_y':     YType,
      'dst_ter':   TType,
      'opaque':    OpqType,
      'vc_id':     VcIdType,
      'payload':   PayloadType,
      'timestamp': TimestampType,
    })
  else:
    return mk_bitstruct( new_name, {
      'src_x':     XType,
      'src_y':     YType,
      'dst_x':     XType,
      'dst_y':     YType,
      'dst_ter':   TType,
      'opaque':    OpqType,
      'payload':   PayloadType,
      'timestamp': TimestampType,
    })

#=========================================================================
# Butterfly packet with timestamp
#=========================================================================

def mk_bfly_pkt_timestamp( k_ary=2, n_fly=2,
                           opaque_nbits=8, vc=0, payload_nbits=32,
                           max_time=10 ):

  IdType   = mk_bits( clog2( k_ary ** n_fly ) )
#  if k_ary == 1:
#    KaryType = Bits1
#  else:
#    KaryType = mk_bits( clog2( k_ary ) )
#  if n_fly == 1:
#    NflyType = Bits1
#  else:
#    NflyType = mk_bits( clog2( n_fly ) )
#  if k_ary ** ( n_fly - 1 ) == 1:
#    RrowType = Bits1
#  else:
#    RrowType = mk_bits( clog2( k_ary ** ( n_fly - 1 ) ) )
  DstType = mk_bits( clog2( k_ary ) * n_fly )
#    DstType = mk_bits( clog2( k_ary ** ( n_fly - 1 ) ) * n_fly )
  OpqType = mk_bits( opaque_nbits )
  PayloadType = mk_bits( payload_nbits )
  TimestampType = mk_bits( clog2(max_time + 1) )

  new_name = f"BflyPacketTimestamp_{k_ary}_{n_fly}_{opaque_nbits}_{vc}_{payload_nbits}"

  if vc > 1:
    VcIdType = mk_bits( clog2( vc ) )

    return mk_bitstruct( new_name, {
      'src':       IdType,
      'dst':       DstType,
      'opaque':    OpqType,
      'vc_id':     VcIdType,
      'payload':   PayloadType,
      'timestamp': TimestampType,
    })
  else:
    return mk_bitstruct( new_name, {
      'src':       IdType,
      'dst':       DstType,
      'opaque':    OpqType,
      'payload':   PayloadType,
      'timestamp': TimestampType,
    })


