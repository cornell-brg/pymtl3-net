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
  def mk_topology( s, network, routers, rows ):
    NORTH = 0
    SOUTH = 1
    WEST  = 2
    EAST  = 3
    SELF  = 4
    cols  = len( routers ) / rows
    for i in range ( len( routers ) ):
      if routers[i].router_id / cols > 0:
        print 'routers[', i, '].router_id: ', routers[i].router_id, '; north: ', routers[routers[i].router_id-rows].router_id
        network.connect( routers[i].send[NORTH], routers[routers[i].router_id-rows].recv[SOUTH] )

      if routers[i].router_id / cols < rows - 1:
        print 'routers[', i, '].router_id: ', routers[i].router_id, '; south: ', routers[routers[i].router_id+rows].router_id
        network.connect( routers[i].send[SOUTH], routers[routers[i].router_id+rows].recv[NORTH] )

      if routers[i].router_id % cols > 0:
        print 'routers[', i, '].router_id: ', routers[i].router_id, '; west: ', routers[routers[i].router_id-1].router_id
        network.connect( routers[i].send[WEST],  routers[routers[i].router_id-1].recv[EAST]  )

      if routers[i].router_id % cols < cols - 1:
        print 'routers[', i, '].router_id: ', routers[i].router_id, '; east: ', routers[routers[i].router_id+1].router_id
        network.connect( routers[i].send[EAST],  routers[routers[i].router_id+1].recv[WEST]  )
 
    for i in range ( len( routers ) / rows ):
      for j in range( rows ):
#        if i != 0:
        print 'making topology here...', routers[i * rows + j].router_id
