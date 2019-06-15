#=========================================================================
# positions.py
#=========================================================================
# Positions definition.
# 
# Author : Yanghui Ou
#   Date : May 20, 2019

from pymtl3 import *

def mk_mesh_pos( mesh_wid, mesh_ht ):
  XType = mk_bits( clog2( mesh_wid ) )
  YType = mk_bits( clog2( mesh_ht  ) )
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

  NflyType = mk_bits( clog2( n_fly + 1 ) )
  RrowType = mk_bits( clog2( k_ary ** ( n_fly - 1 ) + 1) )
  new_name = "BflyPosition_{}_{}".format( k_ary, n_fly )
  new_class = mk_bit_struct( new_name,[
    ( 'row',   RrowType ),
    ( 'stage', NflyType ),
  ])
  return new_class
