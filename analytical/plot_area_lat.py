import matplotlib.pyplot as plt
from dataclasses import dataclass
from lat_model import mesh_cxs1_lat, mesh_cxsx_lat, mesh_cxs3_lat, torus_cxs1_lat, torus_cxsN_lat
from area_model import (
  mesh_area_model as mesh_c1s1_area,
  cmesh4_area_model as mesh_c4s1_area,
  cmesh8_area_model as mesh_c8s1_area,
  mesh_s2d_area_model as mesh_c1s2_area,
  cmesh4_s2d_area_model as mesh_c4s2_area,
  cmesh8_s2d_area_model as mesh_c8s2_area,
  mesh_c1s3_area_model as mesh_c1s3_area,
  mesh_c4s3_area_model as mesh_c4s3_area,
  mesh_c8s3_area_model as mesh_c8s3_area,
  torus_area_model as torus_c1s1_area,
  ctorus4_area_model as torus_c4s1_area,
  ctorus8_area_model as torus_c8s1_area,
)

bw_factor = {
  'mesh-c1e1': 32,
  'mesh-c4e1': 16,
  'mesh-c8e1': 8,
  'mesh-c1e2': 96,
  'mesh-c4e2': 48,
  'mesh-c8e2': 24,
  'mesh-c1e3': 96,
  'mesh-c4e3': 48,
  'mesh-c8e3': 24,

  'torus-c1e1': 64,
  'torus-c4e1': 32,
  'torus-c8e1': 16,
  'torus-c1eN': 96,
  'torus-c4eN': 48,
  'torus-c8eN': 24,
}

tile_dimensions = {
  'c1' : ( 175, 175 ),
  'c4' : ( 365, 365 ),
  'c8' : ( 740, 365 )
}

#-------------------------------------------------------------------------
# Entry
#-------------------------------------------------------------------------

@dataclass
class Entry:
  name  : str
  bw    : int
  chnl  : int
  s_lat : float
  h_lat : float
  area  : float


def get_dataset( msg_size ):
  # mesh-c1s1
  mc1s1  = []
  bc_lst = [ 32, 64, 128, 256, 512 ]
  for bc in bc_lst:
    ser_lat  = msg_size // bc
    h_lat, _ = mesh_cxs1_lat( 16, 16, 1, ser_lat, 1 )
    tile_w, tile_h = tile_dimensions[ 'c1' ]
    area     = mesh_c1s1_area( bc, tile_h, tile_w )
    mc1s1.append(
      Entry(
        name  = 'mesh-c1e1',
        bw    = bc * bw_factor[ 'mesh-c1e1' ],
        chnl  = bc,
        s_lat = ser_lat,
        h_lat = h_lat,
        area  = area,
    ))

  # mesh-c4s1
  mc4s1  = []
  for bc in bc_lst:
    ser_lat  = msg_size // bc
    h_lat, _ = mesh_cxs1_lat( 8, 8, 4, ser_lat, 1 )
    tile_w, tile_h = tile_dimensions[ 'c4' ]
    area     = mesh_c4s1_area( bc, tile_h, tile_w )
    mc4s1.append(
      Entry(
        name  = 'mesh-c4e1',
        bw    = bc * bw_factor[ 'mesh-c4e1' ],
        chnl  = bc,
        s_lat = ser_lat,
        h_lat = h_lat,
        area  = area,
    ))

  # mesh-c8s1
  mc8s1  = []
  for bc in bc_lst:
    ser_lat  = msg_size // bc
    h_lat, _ = mesh_cxs1_lat( 4, 8, 8, ser_lat, 1 )
    tile_w, tile_h = tile_dimensions[ 'c8' ]
    area     = mesh_c8s1_area( bc, tile_h, tile_w )
    mc8s1.append(
      Entry(
        name  = 'mesh-c8e1',
        bw    = bc * bw_factor[ 'mesh-c8e1' ],
        chnl  = bc,
        s_lat = ser_lat,
        h_lat = h_lat,
        area  = area,
    ))

  # mesh-c1s2
  mc1s2  = []
  for bc in bc_lst:
    ser_lat  = msg_size // bc
    h_lat, _ = mesh_cxsx_lat( 16, 16, 1, 2, 1, ser_lat, 1 )
    tile_w, tile_h = tile_dimensions[ 'c1' ]
    area     = mesh_c1s2_area( bc, tile_h, tile_w )
    mc1s2.append(
      Entry(
        name  = 'mesh-c1e2',
        bw    = bc * bw_factor[ 'mesh-c1e2' ],
        chnl  = bc,
        s_lat = ser_lat,
        h_lat = h_lat,
        area  = area,
    ))

  # mesh-c1s2
  mc4s2  = []
  for bc in bc_lst:
    ser_lat  = msg_size // bc
    h_lat, _ = mesh_cxsx_lat( 8, 8, 4, 2, 1, ser_lat, 1 )
    tile_w, tile_h = tile_dimensions[ 'c4' ]
    area     = mesh_c4s2_area( bc, tile_h, tile_w )
    mc4s2.append(
      Entry(
        name  = 'mesh-c4e2',
        bw    = bc * bw_factor[ 'mesh-c4e2' ],
        chnl  = bc,
        s_lat = ser_lat,
        h_lat = h_lat,
        area  = area,
    ))

  # mesh-c8s2
  mc8s2  = []
  for bc in bc_lst:
    ser_lat  = msg_size // bc
    h_lat, _ = mesh_cxsx_lat( 4, 8, 8, 2, 1, ser_lat, 1 )
    tile_w, tile_h = tile_dimensions[ 'c8' ]
    area     = mesh_c8s2_area( bc, tile_h, tile_w )
    mc8s2.append(
      Entry(
        name  = 'mesh-c8e2',
        bw    = bc * bw_factor[ 'mesh-c8e2' ],
        chnl  = bc,
        s_lat = ser_lat,
        h_lat = h_lat,
        area  = area,
    ))

  # mesh-c1s3
  mc1s3  = []
  for bc in bc_lst:
    ser_lat  = msg_size // bc
    h_lat, _ = mesh_cxs3_lat( 16, 16, 1, 1, ser_lat, 1 )
    tile_w, tile_h = tile_dimensions[ 'c1' ]
    area     = mesh_c1s3_area( bc, tile_h, tile_w )
    mc1s3.append(
      Entry(
        name  = 'mesh-c1e3',
        bw    = bc * bw_factor[ 'mesh-c1e3' ],
        chnl  = bc,
        s_lat = ser_lat,
        h_lat = h_lat,
        area  = area,
    ))

  # mesh-c1s3
  mc4s3  = []
  for bc in bc_lst:
    ser_lat  = msg_size // bc
    h_lat, _ = mesh_cxs3_lat( 8, 8, 4, 1, ser_lat, 1 )
    tile_w, tile_h = tile_dimensions[ 'c4' ]
    area     = mesh_c4s3_area( bc, tile_h, tile_w )
    mc4s3.append(
      Entry(
        name  = 'mesh-c4e3',
        bw    = bc * bw_factor[ 'mesh-c4e3' ],
        chnl  = bc,
        s_lat = ser_lat,
        h_lat = h_lat,
        area  = area,
    ))

  # mesh-c8s3
  mc8s3  = []
  for bc in bc_lst:
    ser_lat  = msg_size // bc
    h_lat, _ = mesh_cxs3_lat( 4, 8, 8, 1, ser_lat, 1 )
    tile_w, tile_h = tile_dimensions[ 'c8' ]
    area     = mesh_c8s3_area( bc, tile_h, tile_w )
    mc8s3.append(
      Entry(
        name  = 'mesh-c8e3',
        bw    = bc * bw_factor[ 'mesh-c8e3' ],
        chnl  = bc,
        s_lat = ser_lat,
        h_lat = h_lat,
        area  = area,
    ))


  # tc1s1
  tc1s1  = []
  for bc in bc_lst:
    ser_lat  = msg_size // bc
    h_lat, _ = torus_cxs1_lat( 16, 16, 1, ser_lat, 1 )
    tile_w, tile_h = tile_dimensions[ 'c1' ]
    area     = torus_c1s1_area( bc, tile_h, tile_w )
    tc1s1.append(
      Entry(
        name  = 'torus-c1e1',
        bw    = bc * bw_factor[ 'torus-c1e1' ],
        chnl  = bc,
        s_lat = ser_lat,
        h_lat = h_lat,
        area  = area,
    ))

  # tc4s1
  tc4s1  = []
  for bc in bc_lst:
    ser_lat  = msg_size // bc
    h_lat, _ = torus_cxs1_lat( 8, 8, 4, ser_lat, 1 )
    tile_w, tile_h = tile_dimensions[ 'c4' ]
    area     = torus_c4s1_area( bc, tile_h, tile_w )
    tc4s1.append(
      Entry(
        name  = 'torus-c4e1',
        bw    = bc * bw_factor[ 'torus-c4e1' ],
        chnl  = bc,
        s_lat = ser_lat,
        h_lat = h_lat,
        area  = area,
    ))

  # tc8s1
  tc8s1  = []
  for bc in bc_lst:
    ser_lat  = msg_size // bc
    h_lat, _ = torus_cxs1_lat( 4, 8, 8, ser_lat, 1 )
    tile_w, tile_h = tile_dimensions[ 'c8' ]
    area     = torus_c8s1_area( bc, tile_h, tile_w )
    tc8s1.append(
      Entry(
        name  = 'torus-c8e1',
        bw    = bc * bw_factor[ 'torus-c8e1' ],
        chnl  = bc,
        s_lat = ser_lat,
        h_lat = h_lat,
        area  = area,
    ))



  # # tc1s1
  # tc1sN  = []
  # for bc in bc_lst:
  #   ser_lat  = msg_size // bc
  #   h_lat, _ = torus_cxsN_lat( 16, 16, 1, 1, ser_lat, 1 )
  #   tile_w, tile_h = tile_dimensions[ 'c1' ]
  #   area     = mesh_c1s2_area( bc, tile_h, tile_w )
  #   tc1sN.append(
  #     Entry(
  #       name  = 'torus-c1eN',
  #       bw    = bc * bw_factor[ 'torus-c1eN' ],
  #       chnl  = bc,
  #       s_lat = ser_lat,
  #       h_lat = h_lat,
  #       area  = area,
  #   ))

  # # tc4sN
  # tc4sN  = []
  # for bc in bc_lst:
  #   ser_lat  = msg_size // bc
  #   h_lat, _ = torus_cxsN_lat( 8, 8, 4, 1, ser_lat, 1 )
  #   tile_w, tile_h = tile_dimensions[ 'c4' ]
  #   area     = mesh_c4s2_area( bc, tile_h, tile_w )
  #   tc4sN.append(
  #     Entry(
  #       name  = 'torus-c4eN',
  #       bw    = bc * bw_factor[ 'torus-c4eN' ],
  #       chnl  = bc,
  #       s_lat = ser_lat,
  #       h_lat = h_lat,
  #       area  = area,
  #   ))

  # # tc8sN
  # tc8sN  = []
  # for bc in bc_lst:
  #   ser_lat  = msg_size // bc
  #   h_lat, _ = torus_cxsN_lat( 4, 8, 8, 1, ser_lat, 1 )
  #   tile_w, tile_h = tile_dimensions[ 'c8' ]
  #   area     = mesh_c8s2_area( bc, tile_h, tile_w )
  #   tc8sN.append(
  #     Entry(
  #       name  = 'torus-c8eN',
  #       bw    = bc * bw_factor[ 'torus-c8eN' ],
  #       chnl  = bc,
  #       s_lat = ser_lat,
  #       h_lat = h_lat,
  #       area  = area,
  #   ))

  data_set = [
    mc1s1, mc4s1, mc8s1,
    mc1s2, mc4s2, mc8s2,
    mc1s3, mc4s3, mc8s3,
    tc1s1, tc4s1, tc8s1,
    # tc1sN, tc4sN, tc8sN,
  ]
  return data_set

#-------------------------------------------------------------------------
# misc helper
#-------------------------------------------------------------------------

def assign_style( name ):
  lst = name.split( '-' )
  # skip factor
  marker = 'd' if lst[0]    == 'torus' else \
           'o' if lst[1][3] == '1' else \
           '^' if lst[1][3] == '2' else \
           's'

  line   = '-'  if lst[0]== 'mesh' else \
           '--'
  return f'{line}{marker}'

def assign_color( name ):
  lst = name.split( '-' )
  c = int( lst[1][1] )
  t = lst[0]
  return 'skyblue' if c == 1 else \
         'orange'  if c == 4 else \
         'darkred'

#-------------------------------------------------------------------------
# mk_plot
#-------------------------------------------------------------------------

def mk_plot():
  msg_sizes = [ 64, 512 ]
  bc_lst    = [ 32, 64, 128, 256, 512 ]

  ncols = 3
  nrows = 1
  fig = plt.figure( figsize=(3.5*ncols, 3.5*nrows) )
  axes = [ [ None for _ in range( ncols ) ] for _ in range( nrows )]

  # font = FontProperties()
  # font.set_family( 'serif' )
  # font.set_name( 'Times New Roman' )
  # font.set_size( 13 )

  # limit = [
  #   [ 25, 25 ],
  #   [ 40, 40 ],
  # ]

  #=======================================================================
  # plotting
  #=======================================================================
  # TODO: marker and line styles

  #-----------------------------------------------------------------------
  # bw vs area
  #-----------------------------------------------------------------------

  axes[0][0] = fig.add_subplot( 1, 3, 1 )

  data_sets = get_dataset( 64 )
  for data in data_sets:
    print( f'processing {data[0].name}' )
    bw   = [ x.bw   for x in data if x.area <= 0.3 ]
    area = [ x.area for x in data if x.area <= 0.3 ]
    # lat  = [ x.h_lat + x.s_lat for x in data ]
    style = assign_style( data[0].name )
    color = assign_color( data[0].name )
    axes[0][0].plot( area, bw, style, color=color, label=data[0].name, linewidth=0.5, markersize=4 )
    axes[0][0].spines['top'  ].set_visible( False )
    axes[0][0].spines['right'].set_visible( False )
    # axes[0][0].set_ylim( top=limit[r][c]*1.1, bottom=0 )
    # axes[r][c].grid()
    axes[0][0].grid( color='grey', linestyle='--' )

  #-----------------------------------------------------------------------
  # lat vs area
  #-----------------------------------------------------------------------

  for i, msg_size in enumerate( [ 64, 512 ] ):
    axes[0][i+1] = fig.add_subplot( 1, 3, i+2 )
    data_sets = get_dataset( msg_size )
    for data in data_sets:
      print( f'processing {data[0].name}' )
      area = [ x.area for x in data if x.chnl <= msg_size and x.area <= 0.3 ]
      lat  = [ x.h_lat + x.s_lat for x in data if x.chnl <= msg_size and x.area <= 0.3 ]
      # bw   = [ x.bw for x in data ]
      style = assign_style( data[0].name )
      color = assign_color( data[0].name )
      axes[0][i+1].plot( area, lat, style, color=color, label=data[0].name, linewidth=0.5, markersize=4 )
      axes[0][i+1].spines['top'  ].set_visible( False )
      axes[0][i+1].spines['right'].set_visible( False )
      # axes[0][i+1].set_ylim( top=limit[r][c]*1.1, bottom=0 )
      # axes[r][c].grid()
      axes[0][i+1].grid( color='grey', linestyle='--' )

  # axes[0][0].set_ylabel( 'zero load latency', position=(1, -0.25) ) # TODO: font
  # axes[1][0].set_xlabel( 'bisection bandwidth', position=(1.1, 1) )

  # for c in range( ncols ):
  # axes[0][0].set_title( f'10% area constraints' )
  # axes[0][1].set_title( f'30% area constraints' )

  # axes[0][0].set_ylabel( f'64b message size' )
  # axes[1][0].set_ylabel( f'512b message size' )

  # for r in range( nrows ):
    # axes[r][0].set_xticks( [ 1024, 2048, 3072, 4096 ] )
    # axes[r][1].set_xticks( [ 2048, 4096, 6144, 8192, 10240, 12288 ] )

  # axes[0][0].set_xticklabels( [] )
  # axes[0][1].set_xticklabels( [] )
  # axes[1][0].set_xticklabels( [ '1K', '2K', '3K', '4K' ] )
  # axes[1][1].set_xticklabels( [ '2K', '4K', '6K', '8K', '10K', '12K' ] )

  plt.legend( bbox_to_anchor=(0.75, -0.2), ncol=4 )
  # plt.title( f'msg size: {msg_size}')
  plt.savefig( f'area-bw-lat.pdf', bbox_inches='tight' )


    # area vs lat under bandwidth
    # area_lat_fig = plt.figure( figsize=(6,6) )
    # ax1          = area_lat_fig.add_subplot( 1, 1, 1 )
    # for data in data_sets:
    #   lat  = [ x.h_lat + x.s_lat for x in data if x.area <= 0.3 and x.bw >= 2048 ]
    #   area = [ x.area for x in data if x.area <= 0.3 and x.bw >= 2048 ]
    #   style = assign_style( data[0].name )
    #   ax1.plot( area, lat, style, label=data[0].name )

    # plt.legend()
    # plt.title( f'msg_size: {msg_size}' )
    # plt.savefig( f'area-{msg_size}.pdf', bbox_inches='tight' )

if __name__ == '__main__':
  mk_plot()