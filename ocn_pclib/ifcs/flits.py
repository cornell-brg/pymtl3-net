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
# Generic packet
#=========================================================================

def mk_ring_flit( nrouters=4, nvcs=2, opaque_nbits=8, 
                     payload_nbits=32 ):

  IdType = mk_bits( clog2( nrouters ) )
  TpType = mk_bits( 2 )
  OpqType = mk_bits( opaque_nbits )
  PayloadType = mk_bits( payload_nbits )
  new_name = "RingFlit_{}_{}_{}_{}".format(
    nrouters,
    nvcs,
    opaque_nbits,
    payload_nbits,
  )
  if nvcs > 1:
    VcIdType = mk_bits( clog2( nvcs ) )
    def str_func( self ):
      return "{}>{}:{}:{}:{}:{}".format(
        IdType     ( self.src     ),
        IdType     ( self.dst     ),
        TpType     ( self.fl_type ),
        OpqType    ( self.opaque  ),
        VcIdType   ( self.vc_id   ),
        PayloadType( self.payload ),
      )
    new_class = mk_bit_struct( new_name,[
      ( 'src',     IdType      ),
      ( 'dst',     IdType      ),
      ( 'fl_type', TpType      ),
      ( 'opaque',  OpqType     ),
      ( 'vc_id',   VcIdType    ),
      ( 'payload', PayloadType ),
    ], str_func )

  else:
    def str_func( self ):
      return "{}>{}:{}:{}:{}".format(
        IdType     ( self.src     ),
        IdType     ( self.dst     ),
        TpType     ( self.fl_type ),
        OpqType    ( self.opaque  ),
        PayloadType( self.payload ),
      )
    new_class = mk_bit_struct( new_name,[
      ( 'src',     IdType      ),
      ( 'dst',     IdType      ),
      ( 'fl_type', TpType      ),
      ( 'opaque',  OpqType     ),
      ( 'payload', PayloadType ),
    ], str_func )

  return new_class

#=========================================================================
# mesh flit
#=========================================================================

def mk_mesh_flit( mesh_wid=2, mesh_ht=2, fl_type=0, total_nbits=32,
                 opaque_nbits=8, nvcs=1, payload_nbits=16 ):

  assert mesh_wid > 0 and mesh_ht > 0
  XType       = mk_bits(clog2( mesh_wid )) if mesh_wid != 1 else mk_bits(1)
  YType       = mk_bits(clog2( mesh_ht  )) if mesh_ht  != 1 else mk_bits(1)
  TpType      = mk_bits( 2 )
  OpqType     = mk_bits( opaque_nbits )

  new_name = "MeshFlit_type{}_nbits{}_nvcs{}".format(
    fl_type,
    total_nbits,
    nvcs
  )

  if nvcs > 1:
    VcIdType = mk_bits( clog2( nvcs ) )
    # for HEAD flit:
    if fl_type == 0:
      PayloadType = mk_bits(total_nbits-payload_nbits-
                    clog2(mesh_wid)-clog2(mesh_ht)-2-opaque_nbits-clog2(nvcs))
      def str_func( self ):
        return "({},{})>({},{}):{}:{}:{}:{}".format(
          XType      ( self.src_x   ),
          YType      ( self.src_y   ),
          XType      ( self.dst_x   ),
          YType      ( self.dst_y   ),
          TpType     ( self.fl_type ),
          OpqType    ( self.opaque  ),
          VcIdType   ( self.vc_id   ),
          PayloadType( self.payload ),
        )
      new_class = mk_bit_struct( new_name,[
        ( 'src_x',   XType       ),
        ( 'src_y',   YType       ),
        ( 'dst_x',   XType       ),
        ( 'dst_y',   YType       ),
        ( 'fl_type', TpType      ),
        ( 'opaque',  OpqType     ),
        ( 'vc_id',   VcIdType    ),
        ( 'payload', PayloadType ),
      ], str_func )
    # for BODY, TAIL flits:
    else:
      PayloadType = mk_bits(total_nbits-payload_nbits-
                    clog2(mesh_wid)-clog2(mesh_ht)-2-opaque_nbits-clog2(nvcs))
      def str_func( self ):
        return "{}:{}:{}:{}".format(
          TpType     ( self.fl_type ),
          OpqType    ( self.opaque  ),
          VcIdType   ( self.vc_id   ),
          PayloadType( self.payload ),
        )
      new_class = mk_bit_struct( new_name,[
        ( 'fl_type', TpType      ),
        ( 'opaque',  OpqType     ),
        ( 'vc_id',   VcIdType    ),
        ( 'payload', PayloadType ),
      ], str_func )

  else:
    # for HEAD flit:
    if fl_type == 0:
      PayloadType = mk_bits(total_nbits-payload_nbits-
                    clog2(mesh_wid)-clog2(mesh_ht)-2-opaque_nbits)
      def str_func( self ):
        return "({},{})>({},{}):{}:{}:{}".format(
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

    # for BODY, TAIL flit:
    else:
      PayloadType = mk_bits(total_nbits-payload_nbits-
                    clog2(mesh_wid)-clog2(mesh_ht)-2-opaque_nbits)
      def str_func( self ):
        return "{}:{}:{}".format(
          TpType     ( self.fl_type ),
          OpqType    ( self.opaque  ),
          PayloadType( self.payload ),
        )
      new_class = mk_bit_struct( new_name,[
        ( 'fl_type', TpType      ),
        ( 'opaque',  OpqType     ),
        ( 'payload', PayloadType ),
      ], str_func )
  return new_class

#=========================================================================
# flitisize packet into mesh flits
#=========================================================================

def flitisize_mesh_flit( pkt, mesh_wid=2, mesh_ht=2, 
                         opaque_nbits=8, nvcs=1, payload_nbits=16, fl_size=32 ):

  HeadFlitType = mk_mesh_flit( mesh_wid, mesh_ht, 0, fl_size)
  BodyFlitType = mk_mesh_flit( mesh_wid, mesh_ht, 1, fl_size)
  TailFlitType = mk_mesh_flit( mesh_wid, mesh_ht, 2, fl_size)

  HEAD_CTRL_SIZE = clog2(mesh_wid + mesh_ht + 4 + opaque_nbits + nvcs)
  BODY_CTRL_SIZE = clog2(4 + opaque_nbits + nvcs)
  fl_head_payload_nbits = fl_size - HEAD_CTRL_SIZE
  fl_body_payload_nbits = fl_size - BODY_CTRL_SIZE

  HeadFlitType = mk_mesh_flit( mesh_wid, mesh_ht, fl_type=0, total_nbits=fl_size,
                 opaque_nbits=1, nvcs=1, payload_nbits=fl_head_payload_nbits )
  BodyFlitType = mk_mesh_flit( mesh_wid, mesh_ht, fl_type=1, total_nbits=fl_size,
                 opaque_nbits=1, nvcs=1, payload_nbits=fl_body_payload_nbits )

  current_payload_filled = 0
  head_flit = None
  if payload_nbits <= fl_head_payload_nbits:
    head_flit = HeadFlitType( pkt.src_x, pkt.src_y, pkt.dst_x, pkt.dst_y, 
                              fl_type=0, opaque=0, payload=pkt.payload )
    current_payload_filled += payload_nbits
  else:
    head_flit = HeadFlitType( pkt.src_x, pkt.src_y, pkt.dst_x, pkt.dst_y, 
                              fl_type=0, opaque=0, payload=0 )

  flits = [ had_flit ]
  while current_payload_filled < payload_nbits:
    body_flit = BodyFlitType( fl_type=1, opaque=0, payload=pkt.payload )
    current_payload_filled += fl_body_payload_nbits
    flits.append( body_flit )

  return flits
