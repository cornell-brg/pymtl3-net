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

def mk_mesh_flit( mesh_wid=2, mesh_ht=2, opaque_nbits=8,
                 nvcs=1, payload_nbits=32 ):

  assert mesh_wid > 0 and mesh_ht > 0
  XType       = mk_bits(clog2( mesh_wid )) if mesh_wid != 1 else mk_bits(1)
  YType       = mk_bits(clog2( mesh_ht  )) if mesh_ht  != 1 else mk_bits(1)
  TpType      = mk_bits( 2 )
  OpqType     = mk_bits( opaque_nbits )
  PayloadType = mk_bits( payload_nbits )

  new_name = "MeshPacket_{}x{}_{}_{}_{}".format(
    mesh_wid,
    mesh_ht,
    nvcs,
    opaque_nbits,
    payload_nbits,
  )

  if nvcs > 1:
    VcIdType = mk_bits( clog2( nvcs ) )
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
  else:
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
  return new_class
