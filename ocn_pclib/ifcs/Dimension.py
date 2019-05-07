#=========================================================================
# Dimension.py
#=========================================================================
# Dimension information for each module
#
# Author : Cheng Tan
#   Date : May 7, 2019

from pymtl                 import *
from ocn_pclib.ifcs.Packet import *

import py

#-------------------------------------------------------------------------
# Dimension information used for floorplanning and topology demo 
#-------------------------------------------------------------------------

class Dimension( object ):

  def __init__( s, model ):
    s.model = model
    s.x     = 0
    s.y     = 0
    s.w     = 0
    s.h     = 0

  def __str__( s ):
    return "({},{}|{},{}|{},{})".format( s.x, s.y, s.w, s.h, 
            s.x + s.w, s.y + s.h )

  def floorplan_script( s ):
    return "createFence {} {} {} {} {}".format( s.model.name, s.x, s.y,
            s.x + s.w, s.y + s.h )

  def topology_demo( s ):
    return ( s.x, s.y )
