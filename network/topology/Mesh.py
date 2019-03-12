#=========================================================================
# Mesh.py
#=========================================================================
# Initial implementation of Mesh topology
#
# Author : Cheng Tan
#   Date : Mar 10, 2019

from pymtl import *
from pclib.ifcs.EnRdyIfc      import InEnRdyIfc, OutEnRdyIfc

from network.router.RouterRTL import RouterRTL

class Mesh( RTLComponent ):
  def construct( s ):
    pass

  # Manipulate the input and output ports of routers to connect each other.
  def mkTopology( s, routers ):
    for i in range ( len( routers ) ):
      print 'making topology here...', routers[i].router_id
