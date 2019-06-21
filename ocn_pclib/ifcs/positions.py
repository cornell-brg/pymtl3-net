#=========================================================================
# positions.py
#=========================================================================
# Positions definition.
# 
# Author : Yanghui Ou
#   Date : May 20, 2019

from pymtl3 import *

def mk_mesh_pos( mesh_wid, mesh_ht ):
  assert mesh_wid > 0 and mesh_ht > 0
  XType = mk_bits(clog2( mesh_wid )) if mesh_wid != 1 else mk_bits(1)
  YType = mk_bits(clog2( mesh_ht  )) if mesh_ht  != 1 else mk_bits(1)
  new_name  = "MeshPosition_" + str( mesh_wid ) + "x" + str( mesh_ht )
  new_class = mk_bit_struct( new_name, [
    ( 'pos_x' , XType ),
    ( 'pos_y' , YType )
  ])
  return new_class

def mk_ring_pos( nrouters ):
  assert nrouters > 1
  return mk_bits( clog2( nrouters ) )

#=========================================================================
# Butterfly position
#=========================================================================

def mk_bfly_pos( k_ary=2, n_fly=2 ):

  if n_fly == 1:
    NflyType = Bits1
  else:
    NflyType = mk_bits( clog2( n_fly ) )
  if k_ary ** ( n_fly - 1 ) == 1:
    RrowType = Bits1
  else:
    RrowType = mk_bits( clog2( k_ary ** ( n_fly - 1 ) ) )
  new_name = "BflyPosition_{}_{}".format( k_ary, n_fly )
  new_class = mk_bit_struct( new_name,[
    ( 'row',   RrowType ),
    ( 'stage', NflyType ),
  ])
  return new_class
