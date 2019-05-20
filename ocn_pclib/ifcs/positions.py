from pymtl     import *
from BitStruct import mk_bit_struct

#=========================================================================
# positions.py
#=========================================================================
# Positions definition.
# 
# Author : Yanghui Ou
#   Date : May 20, 2019

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