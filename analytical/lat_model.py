import math
from dijkstar import Graph, find_path

# Assume 1 cycle router delay
def zero_load_latency( avg_r_hop, avg_c_hop, channel_lat, ser_lat ):
  # return avg_r_hop + avg_c_hop * channel_lat + ser_lat
  return avg_r_hop + avg_c_hop * channel_lat
#-------------------------------------------------------------------------
# mesh_c1s1
#-------------------------------------------------------------------------

def mesh_c1s1_lat( ncols, nrows, ser_lat, channel_lat ):
  channel_hops = []
  router_hops  = []
  for src_x in range( ncols ):
    for src_y in range( nrows ):
      for dst_x in range( ncols ):
        for dst_y in range( nrows ):
          dist_y = abs( dst_y - src_y )
          dist_x = abs( dst_x - src_x )
          channel_hops.append( dist_y + dist_x )
          router_hops.append( dist_y + dist_x )
  avg_channel_hop = sum( channel_hops ) / len( channel_hops )
  avg_router_hop  = sum( router_hops ) / len( router_hops )
  return zero_load_latency( avg_router_hop, avg_channel_hop, channel_lat, ser_lat ), ser_lat

#-------------------------------------------------------------------------
# mesh_cxs1
#-------------------------------------------------------------------------

def mesh_cxs1_lat( ncols, nrows, ncores_per_tile, ser_lat, channel_lat ):
  channel_hops = []
  router_hops  = []
  for src_x in range( ncols ):
    for src_y in range( nrows ):
      for src_c in range( ncores_per_tile ):
          for dst_x in range( ncols ):
            for dst_y in range( nrows ):
              for dst_c in range( ncores_per_tile ):
                dist_y = abs( dst_y - src_y )
                dist_x = abs( dst_x - src_x )
                channel_hops.append( dist_y + dist_x )
                router_hops.append( dist_y + dist_x )
  avg_channel_hop = sum( channel_hops ) / len( channel_hops )
  avg_router_hop  = sum( router_hops ) / len( router_hops )
  h_lat = avg_router_hop + avg_channel_hop * channel_lat
  return h_lat, ser_lat

#-------------------------------------------------------------------------
# torus_c1s1
#-------------------------------------------------------------------------

def torus_c1s1_lat( ncols, nrows, ser_lat, channel_lat ):
  channel_hops = []
  router_hops  = []
  for src_x in range( ncols ):
    for src_y in range( nrows ):
      for dst_x in range( ncols ):
        for dst_y in range( nrows ):
          dist_y = min( abs( dst_y - src_y ), nrows - abs( dst_y - src_y ) )
          dist_x = min( abs( dst_x - src_x ), ncols - abs( dst_x - src_x ) )
          channel_hops.append( dist_y + dist_x )
          router_hops.append( dist_y + dist_x )
  avg_channel_hop = sum( channel_hops ) / len( channel_hops )
  avg_router_hop  = sum( router_hops ) / len( router_hops )
  return zero_load_latency( avg_router_hop, avg_channel_hop, channel_lat, ser_lat )


#-------------------------------------------------------------------------
# torus_cxs1
#-------------------------------------------------------------------------

def torus_cxs1_lat( ncols, nrows, ncores_per_tile, ser_lat, channel_lat ):
  channel_hops = []
  router_hops  = []
  for src_x in range( ncols ):
    for src_y in range( nrows ):
       for src_c in range( ncores_per_tile ):
        for dst_x in range( ncols ):
          for dst_y in range( nrows ):
            for dst_c in range( ncores_per_tile ):

              dist_y = min( abs( dst_y - src_y ), nrows - abs( dst_y - src_y ) )
              dist_x = min( abs( dst_x - src_x ), ncols - abs( dst_x - src_x ) )
              channel_hops.append( dist_y + dist_x )
              router_hops.append( dist_y + dist_x )
  avg_channel_hop = sum( channel_hops ) / len( channel_hops )
  avg_router_hop  = sum( router_hops ) / len( router_hops )
  return zero_load_latency( avg_router_hop, avg_channel_hop, channel_lat, ser_lat ), ser_lat


#-------------------------------------------------------------------------
# mesh_cxs2
#-------------------------------------------------------------------------

def mesh_cxs2_lat( ncols, nrows, ncores_per_tile, exp_channel_lat, ser_lat, channel_lat ):
  all_lat     = []
  skip_factor = 2
  for src_x in range( ncols ):
    for src_y in range( nrows ):
      for src_c in range( ncores_per_tile ):
        for dst_x in range( ncols ):
          for dst_y in range( nrows ):
            for dst_c in range( ncores_per_tile ):
              dist_y = abs( dst_y - src_y )
              dist_x = abs( dst_x - src_x )
              exp_chnl_hop_y = dist_y // skip_factor
              exp_chnl_hop_x = dist_x // skip_factor
              chnl_hop_y     = dist_y - exp_chnl_hop_y*skip_factor
              chnl_hop_x     = dist_x - exp_chnl_hop_x*skip_factor
              router_hops    = exp_chnl_hop_y + exp_chnl_hop_x + chnl_hop_y + chnl_hop_x

              cur_lat = router_hops + \
                        ( exp_chnl_hop_y + exp_chnl_hop_x ) * exp_channel_lat + \
                        (chnl_hop_y + chnl_hop_x ) * channel_lat
                        # + ser_lat
              all_lat.append( cur_lat )

  return sum( all_lat ) / len( all_lat ), ser_lat

#-------------------------------------------------------------------------
# mesh_cxs3
#-------------------------------------------------------------------------

def mesh_cxs3_lat( ncols, nrows, ncores_per_tile, exp_channel_lat, ser_lat, channel_lat ):
  all_lat     = []
  skip_factor = 3
  for src_x in range( ncols ):
    for src_y in range( nrows ):
      for src_c in range( ncores_per_tile ):
        for dst_x in range( ncols ):
          for dst_y in range( nrows ):
            for dst_c in range( ncores_per_tile ):
              dist_y = abs( dst_y - src_y )
              dist_x = abs( dst_x - src_x )
              exp_chnl_hop_y = dist_y // skip_factor
              exp_chnl_hop_x = dist_x // skip_factor
              chnl_hop_y     = dist_y - exp_chnl_hop_y*skip_factor
              chnl_hop_x     = dist_x - exp_chnl_hop_x*skip_factor
              router_hops    = exp_chnl_hop_y + exp_chnl_hop_x + chnl_hop_y + chnl_hop_x

              cur_lat = router_hops + \
                        ( exp_chnl_hop_y + exp_chnl_hop_x ) * exp_channel_lat + \
                        (chnl_hop_y + chnl_hop_x ) * channel_lat
                        # + ser_lat
              all_lat.append( cur_lat )

  return sum( all_lat ) / len( all_lat ), ser_lat

#-------------------------------------------------------------------------
# mesh_cxsx
#-------------------------------------------------------------------------

def _get_express_paths( nrouters, skip_factor ):
  exp_paths = []
  cur_id  = 0
  last_id = nrouters-1
  while cur_id < last_id:
    next_id = cur_id + skip_factor
    if next_id <= last_id:
      # if cur_id not in exp_paths:
        # exp_paths.insert( -1, cur_id )
      # if next_id not in exp_paths:
        # exp_paths.append( next_id )
      exp_paths.append( ( cur_id, next_id ) )
    cur_id = next_id - 1
  return exp_paths

def _get_exp_hops( src_id, dst_id, exp_paths ):
  exp_hops     = 0
  channel_hops = 0

  if dst_id == src_id:
    return 0, 0

  elif dst_id > src_id:
    cur_id = src_id
    while cur_id != dst_id:
      exp_found = False
      for src, dst in exp_paths:
        if cur_id == src and dst <= dst_id:
          cur_id = dst
          exp_hops  += 1
          exp_found = True
          break

      if not exp_found:
        cur_id       += 1
        channel_hops += 1

  else:
    cur_id = src_id
    while cur_id != dst_id:
      exp_found = False
      for dst, src in exp_paths:
        if cur_id == src and dst >= dst_id:
          cur_id = dst
          exp_hops  += 1
          exp_found = True
          break

      if not exp_found:
        cur_id       -= 1
        channel_hops += 1

  return exp_hops, channel_hops


def mesh_cxsx_lat( ncols, nrows, ncores_per_tile, skip_factor, exp_channel_lat, ser_lat, channel_lat ):
  all_lat   = []
  x_exp_paths = _get_express_paths( ncols, skip_factor )
  y_exp_paths = _get_express_paths( nrows, skip_factor )

  for src_x in range( ncols ):
    for src_y in range( nrows ):
      for scr_c in range( ncores_per_tile ):
        for dst_x in range( ncols ):
          for dst_y in range( nrows ):
            for dst_c in range( ncores_per_tile ):
              dist_y = abs( dst_y - src_y )
              dist_x = abs( dst_x - src_x )
              exp_chnl_hop_y, chnl_hop_y = _get_exp_hops( src_y, dst_y, y_exp_paths )
              exp_chnl_hop_x, chnl_hop_x = _get_exp_hops( src_x, dst_x, x_exp_paths )
              router_hops = exp_chnl_hop_y + exp_chnl_hop_x + chnl_hop_y + chnl_hop_x

              cur_lat = router_hops + \
                        ( exp_chnl_hop_y + exp_chnl_hop_x ) * exp_channel_lat + \
                        (chnl_hop_y + chnl_hop_x ) * channel_lat
                        # + ser_lat
              all_lat.append( cur_lat )

  return sum( all_lat ) / len( all_lat ), ser_lat

#-------------------------------------------------------------------------
# torus_cxsN_lat
#-------------------------------------------------------------------------

def _get_graph( nrouters ):
  assert nrouters % 2 == 0
  graph = Graph( undirected=True )

  # Normal paths
  for src in range( nrouters-1 ):
    graph.add_edge( src, src+1, (1, 'normal') )
    # graph.add_edge( src, src+1, 1 )

  # express channels
  for src in range( nrouters // 2 ):
    graph.add_edge( src, nrouters-1-src, (1, 'express') )

  for src in range( nrouters // 2 ):
    graph.add_edge( src, nrouters-src, (1, 'express') )
    # graph.add_edge( src, nrouters-1-src, 1 )

  return graph

def _cost_func( u, v, edge, prev_edge ):
  return 1

def _get_hops( src_id, dst_id, graph ):
  exp_hops     = 0
  channel_hops = 0

  path_info = find_path( graph, src_id, dst_id, cost_func = lambda u, v, e, pe: 1 )
  # path_info = find_path( graph, src_id, dst_id )
  for _, ptype in path_info.edges:
    if ptype == 'express':
      exp_hops += 1
    else:
      channel_hops += 1

  return exp_hops, channel_hops

def torus_cxsN_lat( ncols, nrows, ncores_per_tile, exp_channel_lat, ser_lat, channel_lat ):
  all_lat = []
  x_graph = _get_graph( ncols )
  y_graph = _get_graph( nrows )

  for src_x in range( ncols ):
    for src_y in range( nrows ):
      for scr_c in range( ncores_per_tile ):
        for dst_x in range( ncols ):
          for dst_y in range( nrows ):
            for dst_c in range( ncores_per_tile ):
              exp_hop_y, chnl_hop_y = _get_hops( src_y, dst_y, y_graph )
              exp_hop_x, chnl_hop_x = _get_hops( src_x, dst_x, x_graph )
              router_hops = exp_hop_y + chnl_hop_y + exp_hop_x + chnl_hop_x
              cur_lat = router_hops + (exp_hop_y+exp_hop_x)*exp_channel_lat + \
                        (chnl_hop_y+chnl_hop_x)*channel_lat
              all_lat.append( cur_lat )
  return sum( all_lat ) / len( all_lat ), ser_lat

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

if __name__ == '__main__':
  # ser_lat = [ 16, 16, 8, 8, 4, 2, 1 ]
  # ch_lat  = [ 0,  1,  0, 1, 1, 1, 1 ]
  # for ts, tc in zip( ser_lat, ch_lat ):
  #   print( calc_mesh_lat( 8, 8, ts, tc ) )

  # ser_lat = [ 16, 16, 8, 4, 2, 1 ]
  # ch_lat  = [ 0,  1,  1, 1, 1, 1 ]
  # for ts, tc in zip( ser_lat, ch_lat ):
  #   print( calc_cmesh_lat( 8, 8, 4, ts, tc ) )

  # ser_lat = [ 16, 8, 4, 2 ]
  # ch_lat  = [ 1,  1, 1, 1 ]
  # for ts, tc in zip( ser_lat, ch_lat ):
  #   print( calc_torus_lat( 8, 8, ts, tc ) )

  # for tc in [0, 1]:
  #   for ts in [16, 8, 4, 2, 1]:
  #     print( calc_mesh_lat( 16, 16, ts, tc ) )
  #   print()

  # for tc in [0, 1]:
  #   for ts in [16, 8, 4, 2, 1]:
  #     print( calc_mesh_lat( 16, 16, ts, tc ) )
  #     # print( calc_cmesh_lat( 8, 8, 4, ts, tc) )
  #     # print( calc_cmesh_lat( 4, 8, 8, ts, tc ) )
  #     # print( calc_mesh_exp_dense( 16, 16, 2, 0, ts, tc ) )
  #     # print( calc_mesh_exp_dense( 16, 16, 2, 1, ts, tc ) )
  #     # print( calc_mesh_exp_sparse( 16, 16, 2, 0, ts, tc ) )
  #     # print( calc_mesh_exp_sparse( 16, 16, 2, 1, ts, tc ) )
  #     # print( calc_mesh_exp_sparse( 16, 16, 3, 0, ts, tc ) )
  #     # print( calc_mesh_exp_sparse( 16, 16, 3, 1, ts, tc ) )
  #     # print( calc_cmesh_exp_dense( 8, 8, 4, 2, 0, ts, tc ) )
  #     # print( calc_cmesh_exp_dense( 8, 8, 4, 2, 1, ts, tc ) )
  #     # print( calc_cmesh_exp_sparse( 8, 8, 4, 2, 0, ts, tc ) )
  #     # print( calc_cmesh_exp_sparse( 8, 8, 4, 2, 1, ts, tc ) )
  #     # print( calc_cmesh_exp_sparse( 8, 8, 4, 3, 0, ts, tc ) )
  #     # print( calc_cmesh_exp_sparse( 8, 8, 4, 3, 1, ts, tc ) )
    # p = _get_express_paths(16,3)
    # print(p)
    # print(_get_exp_hops(15, 4, p) )

  ncols = 16
  nrows = 16
  # for ts in [16, 8, 4, 2, 1]:
  #   print( mesh_cxsx_lat( 16, 16, 1, 3, 1, ts, 1 ) )

  # print()

  # for ts in [16, 8, 4, 2, 1]:
  #   print( mesh_cxsx_lat( 4, 8, 8, 2, 1, ts, 1 ) )

  # for ts in [16, 8, 4, 2, 1]:
  #   print( mesh_cxs3_lat( 4, 8, 8, 1, ts, 1 ) )

  for ts in [16, 8, 4, 2, 1]:
    print( mesh_c1s1_lat( 16, 16, ts, 0 ) )

  # print()

  # for ts in [16, 8, 4, 2, 1]:
  #   print( torus_cxsN_lat( 16, 16, 1, 1, ts, 1 ) )
  # for ts in [16, 8, 4, 2, 1]:
  #   print( torus_cxs1_lat( 16, 16, 1, ts, 1 ) )

  # for ts in [16, 8, 4, 2, 1]:
  #   print( torus_cxsN_lat( 16, 16, 1, 1, ts, 1 ) )


  # for ts in [16, 8, 4, 2, 1]:
  #   print( mesh_cxsx_lat( 16, 16, 1, 2, 1, ts, 1 ) )


  # for ts in [16, 8, 4, 2, 1]:
  #   print( torus_cxs1_lat( 4, 8, 8, ts, 1 ) )

  # graph = _get_graph( 8 )
  # print( graph )
  # print( find_path( graph, 2, 6, cost_func = lambda u, v, e, pe: 1 ) )