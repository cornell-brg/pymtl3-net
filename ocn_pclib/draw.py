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

  def draw_topology( s, routers, channels ):

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
          edges_bt_routers.append( ( n2, n4 ) )
        elif n1 != n3 and n1 in routers and n3 in routers and n2 == n4:
          edges_bt_routers.append( ( n1, n3 ) )
        elif n2 != n3 and n2 in routers and n3 in routers and n1 == n4:
          edges_bt_routers.append( ( n2, n3 ) )
        elif n1 != n4 and n1 in routers and n4 in routers and n2 == n3:
          edges_bt_routers.append( ( n1, n4 ) )

    for i in routers:
      color.append( 'black' )

    G = nx.Graph()
    G.add_nodes_from( routers  )
    G.add_edges_from( edges_bt_routers )
#    dot_pos = nx.nx_pydot.graphviz_layout(G, prog='dot')
    nx.draw_spring( G, node_color = color )
    plt.savefig("Graph.png", format="PNG")
#    plt.show()
  
  def register_connection( s, node1, node2 ):
    s.edge_pool.append( ( node1, node2 ) )
  
