#=========================================================================
# test_helpers.py
#=========================================================================
# Helper functions for meshnet tests.
#
# Author : Yanghui Ou
#   Date : Apr 30, 2019

from meshnet.directions import * 

def dor_routing( src_x, src_y, dst_x, dst_y,
                 pos_x, pos_y, dimension='x' ):
  tsrc  = 0
  tsink = 0

  # Compute src port
  if src_x == pos_x and src_y == pos_y:
    tsrc = SELF

  elif dimension.lower() == 'y':
    if   src_x == pos_x: tsrc = SOUTH if src_y < pos_y else NORTH
    elif src_x < pos_x:  tsrc = WEST
    else:                tsrc = EAST
      
  elif dimension.lower() == 'x':
    if   src_y == pos_y: tsrc = WEST if src_x < pos_x else EAST
    elif src_y < pos_y:  tsrc = SOUTH
    else:                tsrc = NORTH

  else:
    raise AssertionError( "dimension must be either x or y!" )

  # Compute dst port
  if dst_x == pos_x and dst_y == pos_y:
    tsink = SELF

  elif dimension.lower() == 'y':
    tsink = ( 
      NORTH if dst_y > pos_y else
      SOUTH if dst_y < pos_y else
      EAST  if dst_x > pos_x else
      WEST
    )

  elif dimension.lower() == 'x':
    tsink = ( 
      EAST  if dst_x > pos_x else
      WEST  if dst_x < pos_x else
      NORTH if dst_y > pos_y else
      SOUTH 
    )

  else:
    raise AssertionError( "dimension must be either x or y!" )

  return tsrc, tsink
