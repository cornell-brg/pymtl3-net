import sys

import networkx as nx
from networkx.drawing.nx_agraph import *
from networkx.drawing.layout import *
from networkx.drawing import *
import matplotlib.pyplot as plt

from graphviz import *
import pydot

class DrawGraph( object ):

  def __init__( s ):

    s.edge_pool = []

  def draw_topology( s, name, top, routers, channels ):

    edges_wt_channel = []
    edges_bt_routers = []
    color = []
    size = []

    nodes_routers = []
    nodes = routers + channels


    for (n1, n2) in s.edge_pool:
      if ( n1._dsl.parent_obj in nodes ) and ( n2._dsl.parent_obj in nodes ):
        edges_wt_channel.append( ( n1._dsl.parent_obj, n2._dsl.parent_obj) )

    for (n1, n2) in edges_wt_channel:
      for (n3, n4) in edges_wt_channel:
        if n2 != n4 and n2 in routers and n4 in routers and n1 == n3:
          if (n2, n4) not in edges_bt_routers:
            edges_bt_routers.append(( n2, n4 )) 
        elif n1 != n3 and n1 in routers and n3 in routers and n2 == n4:
          if (n1, n3) not in edges_bt_routers:
            edges_bt_routers.append(( n1, n3 )) 
        elif n2 != n3 and n2 in routers and n3 in routers and n1 == n4:
          if (n2, n3) not in edges_bt_routers:
            edges_bt_routers.append(( n2, n3 )) 
        elif n1 != n4 and n1 in routers and n4 in routers and n2 == n3:
          if (n1, n4) not in edges_bt_routers:
            edges_bt_routers.append(( n1, n4 )) 

 
    top.elaborate_physical()
    if hasattr(top, 'dim'):
      print top.dim
    else:
      print 'no physical...'


    g = Digraph('G', engine = "neato", filename = name + '.gv' )
    base_name  = 'router__'
    edges_name = []
    nodes_name = []

    for i, r in enumerate( routers ):
      g.node( base_name + str(i), pos = '{},{}!'.format(r.pos.pos_x, r.pos.pos_y))

    for p, q in edges_bt_routers:
      name_p = name_q = 'x'
      for i, r in enumerate( routers ):
        if r == p:
          name_p = base_name + str(i)
        elif r == q:
          name_q = base_name + str(i)
      g.edge( name_p, name_q )

    g.attr( overlap = 'false'  )
    g.attr( splines = 'curved' )
    g.view()

  def register_connection( s, node1, node2 ):
    s.edge_pool.append( ( node1, node2 ) )
  
