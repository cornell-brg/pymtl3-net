"""
=========================================================================
flits.py
=========================================================================
Collection of flits definition.

Author : Cheng Tan
  Date : July 12, 2019
"""
from pymtl3 import *

#=========================================================================
# mesh flit
#=========================================================================

def mk_mesh_flit( mesh_wid=2, mesh_ht=2, fl_type=0, opaque_nbits=1, 
                 nvcs=1, total_flit_nbits=32 ):

  assert mesh_wid > 0 and mesh_ht > 0
  XType       = mk_bits(clog2( mesh_wid )) if mesh_wid != 1 else mk_bits(1)
  YType       = mk_bits(clog2( mesh_ht  )) if mesh_ht  != 1 else mk_bits(1)
  TpType      = mk_bits( 2 )
  OpqType     = mk_bits( opaque_nbits )

  new_name = "MeshFlit_{}x{}_type{}_nbits{}_nvcs{}".format(
    mesh_wid,
    mesh_ht,
    fl_type,
    total_flit_nbits,
    nvcs
  )

  if nvcs > 1:
    VcIdType = mk_bits( clog2( nvcs ) )
    PayloadType = mk_bits(total_flit_nbits-
                  clog2(mesh_wid)-clog2(mesh_ht)-2-opaque_nbits-clog2(nvcs))
    def str_func( self ):
      return "({},{})>({},{}):{}:{}:{}:{}".format(
        XType      ( self.src_x   ),
        YType      ( self.src_y   ),
        XType      ( self.dst_x   ),
        YType      ( self.dst_y   ),
        TpType     ( self.fl_type ),
        OpqType    ( self.opaque  ),
        PayloadType( self.payload ),
        VcIdType   ( self.vc_id   ),
      )
    new_class = mk_bit_struct( new_name,[
      ( 'src_x',   XType       ),
      ( 'src_y',   YType       ),
      ( 'dst_x',   XType       ),
      ( 'dst_y',   YType       ),
      ( 'fl_type', TpType      ),
      ( 'opaque',  OpqType     ),
      ( 'payload', PayloadType ),
      ( 'vc_id',   VcIdType    ),
    ], str_func )
  else:
    PayloadType = mk_bits(total_flit_nbits-\
                  clog2(mesh_wid)-clog2(mesh_ht)-2-opaque_nbits)
    def str_func( self ):
      return "({},{})>({},{}):T{}:{}:{}".format(
        XType      ( self.src_x   ),
        YType      ( self.src_y   ),
        XType      ( self.dst_x   ),
        YType      ( self.dst_y   ),
        TpType     ( self.fl_type ),
        OpqType    ( self.opaque  ),
        PayloadType( self.payload ),
      )
    new_class = mk_bit_struct( new_name,[
      ( 'src_x',   XType       ),
      ( 'src_y',   YType       ),
      ( 'dst_x',   XType       ),
      ( 'dst_y',   YType       ),
      ( 'fl_type', TpType      ),
      ( 'opaque',  OpqType     ),
      ( 'payload', PayloadType ),
    ], str_func )
  return new_class

#=========================================================================
# cmesh flit
#=========================================================================

def mk_cmesh_flit( mesh_wid=2, mesh_ht=2, inports=8, outports=8,
                   fl_type=0, opaque_nbits=1, 
                   nvcs=1, total_flit_nbits=32 ):

  assert mesh_wid > 0 and mesh_ht > 0
  XType       = mk_bits(clog2( mesh_wid )) if mesh_wid != 1 else mk_bits(1)
  YType       = mk_bits(clog2( mesh_ht  )) if mesh_ht  != 1 else mk_bits(1)
  TerType     = mk_bits( clog2( outports - 4 ) )
  TpType      = mk_bits( 2 )
  OpqType     = mk_bits( opaque_nbits )

  new_name = "CMeshFlit_{}x{}_{}x{}_type{}_nbits{}_nvcs{}".format(
    mesh_wid,
    mesh_ht,
    inports,
    outports,
    fl_type,
    total_flit_nbits,
    nvcs
  )

  if nvcs > 1:
    VcIdType = mk_bits( clog2( nvcs ) )
    # for HEAD flit:
    if fl_type == 0:
      PayloadType = mk_bits(total_flit_nbits-
                    clog2(mesh_wid)-clog2(mesh_ht)-2-opaque_nbits-clog2(nvcs))
      new_class = mk_bit_struct( new_name,[
        ( 'src_x',   XType       ),
        ( 'src_y',   YType       ),
        ( 'dst_x',   XType       ),
        ( 'dst_y',   YType       ),
        ( 'dst_ter', TerType     ),
        ( 'fl_type', TpType      ),
        ( 'opaque',  OpqType     ),
        ( 'payload', PayloadType ),
        ( 'vc_id',   VcIdType    ),
      ])
    # for BODY, TAIL flits:
    else:
      PayloadType = mk_bits(total_flit_nbits-
                    clog2(mesh_wid)-clog2(mesh_ht)-2-opaque_nbits-clog2(nvcs))
      new_class = mk_bit_struct( new_name,[
        ( 'src_x',   XType       ),
        ( 'src_y',   YType       ),
        ( 'dst_x',   XType       ),
        ( 'dst_y',   YType       ),
        ( 'dst_ter', TerType     ),
        ( 'fl_type', TpType      ),
        ( 'opaque',  OpqType     ),
        ( 'payload', PayloadType ),
        ( 'vc_id',   VcIdType    ),
      ])
  else:
    # for HEAD flit:
    if fl_type == 0:
      PayloadType = mk_bits(total_flit_nbits-\
                    clog2(mesh_wid)-clog2(mesh_ht)-2-opaque_nbits)
      new_class = mk_bit_struct( new_name,[
        ( 'src_x',   XType       ),
        ( 'src_y',   YType       ),
        ( 'dst_x',   XType       ),
        ( 'dst_y',   YType       ),
        ( 'dst_ter', TerType     ),
        ( 'fl_type', TpType      ),
        ( 'opaque',  OpqType     ),
        ( 'payload', PayloadType ),
      ])

    # for BODY, TAIL flit:
    else:
#      PayloadType = mk_bits( total_flit_nbits-2-opaque_nbits )
      PayloadType = mk_bits(total_flit_nbits-\
                    clog2(mesh_wid)-clog2(mesh_ht)-2-opaque_nbits)
      new_class = mk_bit_struct( new_name,[
        ( 'src_x',   XType       ),
        ( 'src_y',   YType       ),
        ( 'dst_x',   XType       ),
        ( 'dst_y',   YType       ),
        ( 'dst_ter', TerType     ),
        ( 'fl_type', TpType      ),
        ( 'opaque',  OpqType     ),
        ( 'payload', PayloadType ),
      ])
  return new_class

#=========================================================================
# Butterfly flit
#=========================================================================

def mk_bfly_flit( k_ary=2, n_fly=2, fl_type=0, opaque_nbits=1, nvcs=0, 
                 total_flit_nbits=32 ):

  IdType    = mk_bits( clog2( k_ary ** n_fly ) )
  Dst_nbits = 0
  if k_ary ** ( n_fly - 1 ) == 1:
    DstType = mk_bits( n_fly )
    dst_nbits = n_fly
  else:
    DstType = mk_bits( clog2( k_ary ) * n_fly )
    dst_nbits = clog2( k_ary ) * n_fly

  TpType      = mk_bits( 2 )
  OpqType     = mk_bits( opaque_nbits )

  new_name = "BlyFlit_{}_{}_type{}_nbits{}_nvcs{}".format(
    k_ary,
    n_fly,
    fl_type,
    total_flit_nbits,
    nvcs
  )

  if nvcs > 1:
    VcIdType = mk_bits( clog2( nvcs ) )
    # for HEAD flit:
    if fl_type == 0:
      PayloadType = mk_bits(total_flit_nbits-
                    clog2(k_ary**n_fly)-dst_nbits-2-opaque_nbits-clog2(nvcs))
      new_class = mk_bit_struct( new_name,[
        ( 'src',     IdType      ),
        ( 'dst',     DstType     ),
        ( 'fl_type', TpType      ),
        ( 'opaque',  OpqType     ),
        ( 'payload', PayloadType ),
        ( 'vc_id',   VcIdType    ),
      ])
    # for BODY, TAIL flits:
    else:
      PayloadType = mk_bits(total_flit_nbits-
                    clog2(k_ary**n_fly)-dst_nbits-2-opaque_nbits-clog2(nvcs))
      new_class = mk_bit_struct( new_name,[
        ( 'src',     IdType      ),
        ( 'dst',     DstType     ),
        ( 'fl_type', TpType      ),
        ( 'opaque',  OpqType     ),
        ( 'payload', PayloadType ),
        ( 'vc_id',   VcIdType    ),
      ])

  else:
    # for HEAD flit:
    if fl_type == 0:
      PayloadType = mk_bits(total_flit_nbits-
                    clog2(k_ary**n_fly)-dst_nbits-2-opaque_nbits)
      def str_func( self ):
        return "({})>({}):{}:{}:{}".format(
          IdType     ( self.src   ),
          DstType    ( self.dst   ),
          TpType     ( self.fl_type ),
          OpqType    ( self.opaque  ),
          PayloadType( self.payload ),
        )
      new_class = mk_bit_struct( new_name,[
        ( 'src',     IdType      ),
        ( 'dst',     DstType     ),
        ( 'fl_type', TpType      ),
        ( 'opaque',  OpqType     ),
        ( 'payload', PayloadType ),
      ], str_func )

    # for BODY, TAIL flit:
    else:
      PayloadType = mk_bits(total_flit_nbits-
                    clog2(k_ary**n_fly)-dst_nbits-2-opaque_nbits)
      def str_func( self ):
        return "({})>({}):{}:{}:{}".format(
          IdType     ( self.src   ),
          DstType    ( self.dst   ),
          TpType     ( self.fl_type ),
          OpqType    ( self.opaque  ),
          PayloadType( self.payload ),
        )
      new_class = mk_bit_struct( new_name,[
        ( 'src',     IdType      ),
        ( 'dst',     DstType     ),
        ( 'fl_type', TpType      ),
        ( 'opaque',  OpqType     ),
        ( 'payload', PayloadType ),
      ], str_func )
  return new_class

#=========================================================================
# flitisize packet into mesh flits
#=========================================================================

def flitisize_mesh_flit( pkt, mesh_wid=2, mesh_ht=2, opaque_nbits=1, nvcs=1, 
                         pkt_payload_nbits=16, fl_size=32 ):

  HEAD_CTRL_SIZE = clog2(mesh_wid + mesh_ht + 4 + nvcs) + opaque_nbits
  BODY_CTRL_SIZE = clog2(mesh_wid + mesh_ht + 4 + nvcs) + opaque_nbits
#  BODY_CTRL_SIZE = clog2(4 + nvcs) + opaque_nbits
  fl_head_payload_nbits = fl_size - HEAD_CTRL_SIZE
  fl_body_payload_nbits = fl_size - BODY_CTRL_SIZE

  HeadFlitType = mk_mesh_flit( mesh_wid, mesh_ht, fl_type=0,
                 opaque_nbits=opaque_nbits, nvcs=nvcs, total_flit_nbits=fl_size )
  BodyFlitType = mk_mesh_flit( mesh_wid, mesh_ht, fl_type=1,
                 opaque_nbits=opaque_nbits, nvcs=nvcs, total_flit_nbits=fl_size )

  current_payload_filled = 0
  head_flit = None
  flits = []
  if pkt_payload_nbits <= fl_head_payload_nbits:
    head_flit = HeadFlitType( pkt.src_x, pkt.src_y, pkt.dst_x, pkt.dst_y, 
                              fl_type=0, opaque=0, payload=pkt.payload )
    flits.append( head_flit )
  else:
    head_flit = HeadFlitType( pkt.src_x, pkt.src_y, pkt.dst_x, pkt.dst_y, 
                              fl_type=0, opaque=0, payload=0 )

    flits.append( head_flit )
    PktPayloadType = mk_bits( pkt_payload_nbits )
    pkt_payload = PktPayloadType( pkt.payload )
    while current_payload_filled < pkt_payload_nbits:
      LOWER = current_payload_filled
      UPPER = current_payload_filled + fl_body_payload_nbits
      if UPPER > pkt_payload_nbits:
        UPPER = pkt_payload_nbits
      body_flit = BodyFlitType( pkt.src_x, pkt.src_y, pkt.dst_x, pkt.dst_y,
                  fl_type=1, opaque=0, payload=pkt_payload[ LOWER : UPPER ] )
      current_payload_filled += fl_body_payload_nbits
      flits.append( body_flit )

  return flits

#=========================================================================
# flitisize packet into cmesh flits
#=========================================================================

def flitisize_cmesh_flit( pkt, mesh_wid=2, mesh_ht=2, 
                          inports=8, outports=8,
                          opaque_nbits=1, nvcs=1,
                          pkt_payload_nbits=16, fl_size=32 ):

  HEAD_CTRL_SIZE = clog2(mesh_wid + mesh_ht + outports + 4 + nvcs) + opaque_nbits
  BODY_CTRL_SIZE = clog2(mesh_wid + mesh_ht + outports + 4 + nvcs) + opaque_nbits
#  BODY_CTRL_SIZE = clog2(4 + nvcs) + opaque_nbits
  fl_head_payload_nbits = fl_size - HEAD_CTRL_SIZE
  fl_body_payload_nbits = fl_size - BODY_CTRL_SIZE

  HeadFlitType = mk_cmesh_flit( mesh_wid, mesh_ht, inports, outports, fl_type=0,
                 opaque_nbits=opaque_nbits, nvcs=nvcs, total_flit_nbits=fl_size )
  BodyFlitType = mk_cmesh_flit( mesh_wid, mesh_ht, inports, outports, fl_type=1,
                 opaque_nbits=opaque_nbits, nvcs=nvcs, total_flit_nbits=fl_size )

  current_payload_filled = 0
  head_flit = None
  flits = []
  if pkt_payload_nbits <= fl_head_payload_nbits:
    head_flit = HeadFlitType( pkt.src_x, pkt.src_y, pkt.dst_x, pkt.dst_y,
                              pkt.dst_ter, fl_type=0, opaque=0, payload=pkt.payload )
    flits.append( head_flit )
  else:
    head_flit = HeadFlitType( pkt.src_x, pkt.src_y, pkt.dst_x, pkt.dst_y,
                              pkt.dst_ter, fl_type=0, opaque=0, payload=0 )

    flits.append( head_flit )
    PktPayloadType = mk_bits( pkt_payload_nbits )
    pkt_payload = PktPayloadType( pkt.payload )
    while current_payload_filled < pkt_payload_nbits:
      LOWER = current_payload_filled
      UPPER = current_payload_filled + fl_body_payload_nbits
      if UPPER > pkt_payload_nbits:
        UPPER = pkt_payload_nbits
      body_flit = BodyFlitType( pkt.src_x, pkt.src_y, pkt.dst_x, pkt.dst_y,
                  pkt.dst_ter, fl_type=1, opaque=0, 
                  payload=pkt_payload[ LOWER : UPPER ] )
      current_payload_filled += fl_body_payload_nbits
      flits.append( body_flit )

  return flits

#=========================================================================
# flitisize packet into Bfly flits
#=========================================================================

def flitisize_bfly_flit( pkt, k_ary=2, n_fly=2, 
                         opaque_nbits=1, nvcs=1,
                         pkt_payload_nbits=16, fl_size=32 ):

  if k_ary ** ( n_fly - 1 ) == 1:
    dst_nbits = n_fly
  else:
    dst_nbits = clog2( k_ary ) * n_fly
  HEAD_CTRL_SIZE = clog2(k_ary**n_fly)+dst_nbits+2+opaque_nbits+clog2(nvcs)
  BODY_CTRL_SIZE = clog2(k_ary**n_fly)+dst_nbits+2+opaque_nbits+clog2(nvcs)
#  BODY_CTRL_SIZE = 2 + opaque_nbits + clog2(nvcs)
  fl_head_payload_nbits = fl_size - HEAD_CTRL_SIZE
  fl_body_payload_nbits = fl_size - BODY_CTRL_SIZE

  HeadFlitType = mk_bfly_flit( k_ary, n_fly, fl_type=0,
                 opaque_nbits=opaque_nbits, nvcs=nvcs, total_flit_nbits=fl_size )
  BodyFlitType = mk_bfly_flit( k_ary, n_fly, fl_type=1,
                 opaque_nbits=opaque_nbits, nvcs=nvcs, total_flit_nbits=fl_size )

  current_payload_filled = 0
  head_flit = None
  flits = []
  if pkt_payload_nbits <= fl_head_payload_nbits:
    head_flit = HeadFlitType( pkt.src, pkt.dst, fl_type=0, opaque=0, 
                              payload=pkt.payload )
    flits.append( head_flit )
  else:
    head_flit = HeadFlitType( pkt.src, pkt.dst, fl_type=0, opaque=0, 
                              payload=0 )

    flits.append( head_flit )
    PktPayloadType = mk_bits( pkt_payload_nbits )
    pkt_payload = PktPayloadType( pkt.payload )
    while current_payload_filled < pkt_payload_nbits:
      LOWER = current_payload_filled
      UPPER = current_payload_filled + fl_body_payload_nbits
      if UPPER > pkt_payload_nbits:
        UPPER = pkt_payload_nbits
      body_flit = BodyFlitType( pkt.src, pkt.dst, fl_type=1, opaque=0, 
                  payload=pkt_payload[ LOWER : UPPER ] )
      current_payload_filled += fl_body_payload_nbits
      flits.append( body_flit )

  return flits
