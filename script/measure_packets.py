"""
==========================================================================
measure_packets.py
==========================================================================
Packets for network measurement.

Author : Yanghui Ou
  Date : Sep 24, 2019
"""
from pymtl3 import *

#-------------------------------------------------------------------------
# mk_ring_pkt
#-------------------------------------------------------------------------

def mk_ring_pkt( nrouters=4, nvcs=2, payload_nbits=32 ):
  id_type = mk_bits( clog2( nrouters ) )
  v_type  = mk_bits( clog2( nvcs     ) )
  p_type  = mk_bits( payload_nbits     )
  new_name = f'RingMeasurePkt_{nrouters}_{nvcs}_{payload_nbits}'
  new_class = mk_bit_struct( new_name, [
    ( 'src',     id_type ),
    ( 'dst',     id_type ),
    ( 'vc_id',   v_type  ),
    ( 'measure', Bits1   ),
    ( 'payload', p_type  ),
  ])
  return new_class

#-------------------------------------------------------------------------
# mk_ring_pkt
#-------------------------------------------------------------------------

def mk_mesh_pkt( ncols=2, nrows=2, nvcs=1, payload_nbits=32 ):
  x_type = mk_bits( clog2( ncols ) )
  y_type = mk_bits( clog2( nrows ) )
  p_type = mk_bits( payload_nbits  )

  new_name = f'MeshMeasurePkt_{ncols}_{nrows}_{nvcs}_{payload_nbits}'
  if nvcs > 1:
    v_type = mk_bits( clog2( nvcs ) )
    new_class = mk_bit_struct( new_name, [
      ( 'src_x',   x_type ),
      ( 'src_y',   y_type ),
      ( 'dst_x',   x_type ),
      ( 'dst_y',   y_type ),
      ( 'vc_id',   v_type ),
      ( 'measure', Bits1  ),
      ( 'payload', p_type ),
    ])
  else:
    new_class = mk_bit_struct( new_name, [
      ( 'src_x',   x_type ),
      ( 'src_y',   y_type ),
      ( 'dst_x',   x_type ),
      ( 'dst_y',   y_type ),
      ( 'measure', Bits1  ),
      ( 'payload', p_type ),
    ])

  return new_class
