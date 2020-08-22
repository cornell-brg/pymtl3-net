'''
==========================================================================
area_model.py
==========================================================================
'''
import math
import scipy
import numpy as np
from scipy.interpolate import interp1d
import argparse

from ubmark_data import db_850 as db

radix_dict = {
  'mesh'       : 5,
  'torus'      : 5,
  'cmesh4'     : 8,
  'cmesh8'     : 12,
  'mesh-s2d'   : 9,
  'cmesh4-s2d' : 12,
}

torus_radix_factor = 1
#-------------------------------------------------------------------------
# estimate_router_area
#-------------------------------------------------------------------------

def estimate_router_area( db, radix, channel_nbits ):

  # find all points with the corresponding channel_nbits

  data = [ record for record in db if record.channel_nbits == channel_nbits ]
  x = [ r.radix for r in data ]
  y = [ r.area  for r in data ]

  # Interpolate

  if radix <= max( x ):
    fn = interp1d( x, y, kind='quadratic' )
    return fn( radix )

  # Extrapolate

  else:
    fn = np.polyfit( x, y, 2 )
    return np.polyval( fn, radix )

#-------------------------------------------------------------------------
# channel_width_model
#-------------------------------------------------------------------------

def channel_width_model( nbits ):
  return nbits/64*5

#-------------------------------------------------------------------------
# mesh_c1s1
#-------------------------------------------------------------------------

def _mesh_area( tile_w, tile_h, channel_w, router_h, router_w ):
  tile_area   = tile_w * tile_h
  router_area = router_w*router_h + channel_w*(tile_h-router_h) + channel_w*(tile_w-router_w)
  return router_area/tile_area

def mesh_area_model( channel_nbits, tile_h, tile_w ):
  # TODO: choose a db
  mesh_db     = db
  radix       = 5
  router_area = estimate_router_area( mesh_db, radix, channel_nbits )
  router_w    = math.sqrt( router_area )
  router_h    = router_w
  channel_w   = channel_width_model( channel_nbits )
  return _mesh_area( tile_w, tile_h, channel_w, router_h, router_w )

#-------------------------------------------------------------------------
# mesh_c4s1
#-------------------------------------------------------------------------

def _cmesh4_area( tile_w, tile_h, channel_w, router_h, router_w ):
  router_area  = router_w*router_h
  channel_area = channel_w*(tile_w-router_w) + channel_w*(tile_h-router_h)
  return ( router_area + channel_area ) / ( tile_w * tile_h )

def cmesh4_area_model( channel_nbits, tile_h, tile_w ):
  cmesh4_db = db
  radix = 8
  router_area = estimate_router_area( cmesh4_db, radix, channel_nbits )
  router_w = router_h = math.sqrt( router_area )
  channel_w = channel_width_model( channel_nbits )
  return _cmesh4_area( tile_w, tile_h, channel_w, router_h, router_w )

#-------------------------------------------------------------------------
# mesh_c8s1
#-------------------------------------------------------------------------

def _cmesh8_area( tile_w, tile_h, channel_w, router_h, router_w ):
  router_area  = router_w*router_h
  channel_area = channel_w*(tile_w-router_w) + channel_w*(tile_h-router_h)
  return ( router_area + channel_area ) / ( tile_w * tile_h )

def cmesh8_area_model( channel_nbits, tile_h, tile_w ):
  cmesh4_db = db
  radix = 12
  router_area = estimate_router_area( cmesh4_db, radix, channel_nbits )
  router_w = router_h = math.sqrt( router_area )
  channel_w = channel_width_model( channel_nbits )
  return _cmesh8_area( tile_w, tile_h, channel_w, router_h, router_w )

#-------------------------------------------------------------------------
# mesh_c1s2
#-------------------------------------------------------------------------

def _mesh_s2d_area( tile_w, tile_h, channel_w, router_h, router_w ):
  assert channel_w*3 <= router_h
  assert channel_w*3 <= router_w
  router_area  = router_w*router_h
  channel_area = 3*(channel_w*(tile_w-router_w) + channel_w*(tile_h-router_h))
  return ( router_area + channel_area ) / ( tile_w * tile_h )

def mesh_s2d_area_model( channel_nbits, tile_h, tile_w ):
  mesh_db = db
  radix   = 9
  router_area = estimate_router_area( mesh_db, radix, channel_nbits )
  router_w = router_h = math.sqrt( router_area )
  channel_w = channel_width_model( channel_nbits )
  return _mesh_s2d_area( tile_w, tile_h, channel_w, router_h, router_w )

#-------------------------------------------------------------------------
# mesh_c4s2
#-------------------------------------------------------------------------

def _cmesh4_s2d_area( tile_w, tile_h, channel_w, router_h, router_w ):
  assert channel_w*3 <= router_h
  assert channel_w*3 <= router_w
  router_area  = router_w*router_h
  channel_area = 3*(channel_w*(tile_w-router_w) + channel_w*(tile_h-router_h))
  return ( router_area + channel_area ) / ( tile_w * tile_h )

def cmesh4_s2d_area_model( channel_nbits, tile_h, tile_w ):
  mesh_db = db
  radix   = 12
  router_area = estimate_router_area( mesh_db, radix, channel_nbits )
  router_w = router_h = math.sqrt( router_area )
  channel_w = channel_width_model( channel_nbits )
  return _cmesh4_s2d_area( tile_w, tile_h, channel_w, router_h, router_w )

#-------------------------------------------------------------------------
# mesh8_c8s2
#-------------------------------------------------------------------------

def _cmesh8_s2d_area( tile_w, tile_h, channel_w, router_h, router_w ):
  assert channel_w*3 <= router_h
  assert channel_w*3 <= router_w
  router_area  = router_w*router_h
  channel_area = 3*(channel_w*(tile_w-router_w) + channel_w*(tile_h-router_h))
  return ( router_area + channel_area ) / ( tile_w * tile_h )

def cmesh8_s2d_area_model( channel_nbits, tile_h, tile_w ):
  mesh_db = db
  radix   = 16
  router_area = estimate_router_area( mesh_db, radix, channel_nbits )
  router_w = router_h = math.sqrt( router_area )
  channel_w = channel_width_model( channel_nbits )
  return _cmesh8_s2d_area( tile_w, tile_h, channel_w, router_h, router_w )

#-------------------------------------------------------------------------
# mesh_c1s3
#-------------------------------------------------------------------------

def _mesh_c1s3_area( tile_w, tile_h, channel_w, router_h, router_w ):
  assert channel_w*3 <= router_h
  assert channel_w*3 <= router_w
  router_area  = router_w*router_h
  channel_area = 4*(channel_w*(tile_w-router_w) + channel_w*(tile_h-router_h))
  return ( router_area + channel_area ) / ( tile_w * tile_h )

def mesh_c1s3_area_model( channel_nbits, tile_h, tile_w ):
  mesh_db = db
  radix   = 9
  router_area = estimate_router_area( mesh_db, radix, channel_nbits )
  router_w = router_h = math.sqrt( router_area )
  channel_w = channel_width_model( channel_nbits )
  return _mesh_c1s3_area( tile_w, tile_h, channel_w, router_h, router_w )

#-------------------------------------------------------------------------
# mesh_c4s3
#-------------------------------------------------------------------------

def _mesh_c4s3_area( tile_w, tile_h, channel_w, router_h, router_w ):
  assert channel_w*4 <= router_h
  assert channel_w*4 <= router_w
  router_area  = router_w*router_h
  channel_area = 4*(channel_w*(tile_w-router_w) + channel_w*(tile_h-router_h))
  return ( router_area + channel_area ) / ( tile_w * tile_h )

def mesh_c4s3_area_model( channel_nbits, tile_h, tile_w ):
  mesh_db = db
  radix   = 12
  router_area = estimate_router_area( mesh_db, radix, channel_nbits )
  router_w = router_h = math.sqrt( router_area )
  channel_w = channel_width_model( channel_nbits )
  return _mesh_c4s3_area( tile_w, tile_h, channel_w, router_h, router_w )

#-------------------------------------------------------------------------
# mesh_c8s3
#-------------------------------------------------------------------------

def _mesh_c8s3_area( tile_w, tile_h, channel_w, router_h, router_w ):
  assert channel_w*4 <= router_h
  assert channel_w*4 <= router_w
  router_area  = router_w*router_h
  channel_area = 4*(channel_w*(tile_w-router_w) + channel_w*(tile_h-router_h))
  return ( router_area + channel_area ) / ( tile_w * tile_h )

def mesh_c8s3_area_model( channel_nbits, tile_h, tile_w ):
  mesh_db = db
  radix   = 16
  router_area = estimate_router_area( mesh_db, radix, channel_nbits )
  router_w = router_h = math.sqrt( router_area )
  channel_w = channel_width_model( channel_nbits )
  return _mesh_c8s3_area( tile_w, tile_h, channel_w, router_h, router_w )

#-------------------------------------------------------------------------
# torus_c1s1
#-------------------------------------------------------------------------

def _torus_area( tile_w, tile_h, channel_w, router_h, router_w ):
  tile_area   = tile_w * tile_h
  router_area = router_w*router_h
  channel_area = 2 * ( channel_w*(tile_h-router_h) + channel_w*(tile_w-router_w) )
  return ( router_area + channel_area )/tile_area

def torus_area_model( channel_nbits, tile_h, tile_w ):
  # TODO: choose a db
  torus_db    = db
  radix       = 5 * torus_radix_factor
  router_area = estimate_router_area( torus_db, radix, channel_nbits )
  router_w    = math.sqrt( router_area )
  router_h    = router_w
  channel_w   = channel_width_model( channel_nbits )
  return _torus_area( tile_w, tile_h, channel_w, router_h, router_w )


#-------------------------------------------------------------------------
# torus_c4s1
#-------------------------------------------------------------------------

def _ctorus4_area( tile_w, tile_h, channel_w, router_h, router_w ):
  router_area  = router_w*router_h
  channel_area = 2 * ( channel_w*(tile_h-router_h) + channel_w*(tile_w-router_w) )
  return ( router_area + channel_area ) / ( tile_w * tile_h )

def ctorus4_area_model( channel_nbits, tile_h, tile_w ):
  ctorus4_db = db
  radix = 8 * torus_radix_factor
  router_area = estimate_router_area( ctorus4_db, radix, channel_nbits )
  router_w = router_h = math.sqrt( router_area )
  channel_w = channel_width_model( channel_nbits )
  return _ctorus4_area( tile_w, tile_h, channel_w, router_h, router_w )


#-------------------------------------------------------------------------
# torus_c8s1
#-------------------------------------------------------------------------

def _ctorus8_area( tile_w, tile_h, channel_w, router_h, router_w ):
  router_area  = router_w*router_h
  channel_area = 2 * ( channel_w*(tile_h-router_h) + channel_w*(tile_w-router_w) )
  return ( router_area + channel_area ) / ( tile_w * tile_h )

def ctorus8_area_model( channel_nbits, tile_h, tile_w ):
  ctorus8_db = db
  radix = 12 * torus_radix_factor
  router_area = estimate_router_area( ctorus8_db, radix, channel_nbits )
  router_w = router_h = math.sqrt( router_area )
  channel_w = channel_width_model( channel_nbits )
  return _ctorus8_area( tile_w, tile_h, channel_w, router_h, router_w )

#-------------------------------------------------------------------------
# torus_c1s2
#-------------------------------------------------------------------------

def _torus_c1s2_area( tile_w, tile_h, channel_w, router_h, router_w ):
  tile_area   = tile_w * tile_h
  router_area = router_w*router_h
  channel_area = 3 * ( channel_w*(tile_h-router_h) + channel_w*(tile_w-router_w) )
  return ( router_area + channel_area )/tile_area

def torus_c1s2_area_model( channel_nbits, tile_h, tile_w ):
  # TODO: choose a db
  torus_db    = db
  radix       = 9 * torus_radix_factor
  router_area = estimate_router_area( torus_db, radix, channel_nbits )
  router_w    = math.sqrt( router_area )
  router_h    = router_w
  channel_w   = channel_width_model( channel_nbits )
  return _torus_area( tile_w, tile_h, channel_w, router_h, router_w )

#-------------------------------------------------------------------------
# torus_c4s2
#-------------------------------------------------------------------------

def _torus_c4s2_area( tile_w, tile_h, channel_w, router_h, router_w ):
  router_area  = router_w*router_h
  channel_area = 3 * ( channel_w*(tile_h-router_h) + channel_w*(tile_w-router_w) )
  return ( router_area + channel_area ) / ( tile_w * tile_h )

def torus_c4s2_area_model( channel_nbits, tile_h, tile_w ):
  ctorus4_db = db
  radix = 12 * torus_radix_factor
  router_area = estimate_router_area( ctorus4_db, radix, channel_nbits )
  router_w = router_h = math.sqrt( router_area )
  channel_w = channel_width_model( channel_nbits )
  return _ctorus4_area( tile_w, tile_h, channel_w, router_h, router_w )

#-------------------------------------------------------------------------
# torus_c8s2
#-------------------------------------------------------------------------

def _torus_c8s2_area( tile_w, tile_h, channel_w, router_h, router_w ):
  router_area  = router_w*router_h
  channel_area = 3 * ( channel_w*(tile_h-router_h) + channel_w*(tile_w-router_w) )
  return ( router_area + channel_area ) / ( tile_w * tile_h )

def torus_c8s2_area_model( channel_nbits, tile_h, tile_w ):
  ctorus4_db = db
  radix = 8 * torus_radix_factor
  router_area = estimate_router_area( ctorus4_db, radix, channel_nbits )
  router_w = router_h = math.sqrt( router_area )
  channel_w = channel_width_model( channel_nbits )
  return _ctorus4_area( tile_w, tile_h, channel_w, router_h, router_w )


#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

if __name__ == '__main__':
  # print( estimate_router_area( db, 8, 512 ) )

  # # print( '-'*74 )
  # # print( 'mesh')
  # # print( '-'*74 )
  # for nbits in [ 32, 64, 128, 256, 512 ]:
  #   print( mesh_area_model( nbits, 175, 175 ) )

  # # print( '-'*74 )
  # # print( 'cmesh4')
  # # print( '-'*74 )
  # for nbits in [ 32, 64, 128, 256, 512 ]:
  #   print( cmesh4_area_model( nbits, 375, 375 ) )

  # # print( '-'*74 )
  # # print( 'cmesh8')
  # # print( '-'*74 )
  # for nbits in [ 32, 64, 128, 256, 512 ]:
  #   print( cmesh8_area_model( nbits, 750, 350 ) )

  # # print( '-'*74 )
  # # print( 'mesh_s2d')
  # # print( '-'*74 )
  # for nbits in [ 32, 64, 128, 256, 512 ]:
  #   print( mesh_s2d_area_model( nbits, 175, 175 ) )

  # # print( '-'*74 )
  # # print( 'cmesh4_s2d')
  # # print( '-'*74 )
  # for nbits in [ 32, 64, 128, 256, 512 ]:
  #   print( cmesh4_s2d_area_model( nbits, 375, 375 ) )

  # # print( '-'*74 )
  # # print( 'cmesh8_s2d')
  # # print( '-'*74 )
  # for nbits in [ 32, 64, 128, 256, 512 ]:
  #   print( cmesh8_s2d_area_model( nbits, 750, 375 ) )

  # # print( '-'*74 )
  # # print( 'mesh_s2d')
  # # print( '-'*74 )
  # for nbits in [ 32, 64, 128, 256, 512 ]:
  #   print( mesh_s2d_area_model( nbits, 175, 175 ) )

  # # print( '-'*74 )
  # # print( 'cmesh4_s2d')
  # # print( '-'*74 )
  # for nbits in [ 32, 64, 128, 256, 512 ]:
  #   print( cmesh4_s2d_area_model( nbits, 375, 375 ) )

  # # print( '-'*74 )
  # # print( 'cmesh8_s2d')
  # # print( '-'*74 )
  # for nbits in [ 32, 64, 128, 256, 512 ]:
  #   print( cmesh8_s2d_area_model( nbits, 750, 375 ) )



  # # print( '-'*74 )
  # # print( 'torus')
  # # print( '-'*74 )
  # for nbits in [ 32, 64, 128, 256, 512 ]:
  #   print( torus_area_model( nbits, 175, 175 ) )

  # # print( '-'*74 )
  # # print( 'ctorus4')
  # # print( '-'*74 )
  # for nbits in [ 32, 64, 128, 256, 512 ]:
  #   print( ctorus4_area_model( nbits, 375, 375 ) )



  # # print( '-'*74 )
  # # print( 'ctorus8')
  # # print( '-'*74 )
  # for nbits in [ 32, 64, 128, 256, 512 ]:
  #   print( ctorus8_area_model( nbits, 350,750 ) )


  # for nbits in [ 32, 64, 128, 256, 512 ]:
  #   print( torus_c1s2_area_model( nbits, 175, 175 ) )

  # for nbits in [ 32, 64, 128, 256, 512 ]:
  #   print( torus_c4s2_area_model( nbits, 375, 375 ) )

  for nbits in [ 32, 64, 128, 256, 512 ]:
    print( mesh_s2d_area_model( nbits, 175, 175 ) )

  print()

  for nbits in [ 32, 64, 128, 256, 512 ]:
    print( mesh_s2d_area_model( nbits, 365, 365 ) )

  print()

  for nbits in [ 32, 64, 128, 256, 512 ]:
    print( mesh_s2d_area_model( nbits, 740, 365 ) )

  for nbits in [ 32, 64, 128, 256, 512 ]:
    print( mesh_c1s3_area_model( nbits, 175, 175 ) )

  print()

  for nbits in [ 32, 64, 128, 256, 512 ]:
    print( mesh_c4s3_area_model( nbits, 365, 365 ) )

  print()

  for nbits in [ 32, 64, 128, 256, 512 ]:
    print( mesh_c8s3_area_model( nbits, 740, 365 ) )