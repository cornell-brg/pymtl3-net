#=========================================================================
# positions.py
#=========================================================================
# Positions definition.
#
# Author : Yanghui Ou
#   Date : May 20, 2019

from pymtl3 import *

def mk_mesh_pos( mesh_width, mesh_height ):
  assert mesh_width > 0 and mesh_height > 0

  XType = mk_bits(clog2( mesh_width  )) if mesh_width  != 1 else Bits1
  YType = mk_bits(clog2( mesh_height )) if mesh_height != 1 else Bits1

  return mk_bitstruct( f"MeshPosition_{mesh_width}x{mesh_height}", {
    'pos_x': XType,
    'pos_y': YType
  })

def mk_ring_pos( nrouters ):
  assert nrouters > 1
  return mk_bits( clog2( nrouters ) )

#=========================================================================
# Butterfly position
#=========================================================================

def mk_bfly_pos( k_ary=2, n_fly=2 ):
  assert n_fly > 0 and k_ary > 0

  row = k_ary ** ( n_fly - 1 )
  NflyType = mk_bits( clog2( n_fly ) ) if n_fly != 1 else Bits1
  RrowType = mk_bits( clog2( k_ary ** ( n_fly - 1 ) ) ) if row != 1 else Bits1

  return mk_bitstruct( f"BflyPosition_{k_ary}_{n_fly}", {
    'row':   RrowType,
    'stage': NflyType,
  })
