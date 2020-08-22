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
from scipy.interpolate import interp1d
import numpy as np
from matplotlib.font_manager import FontProperties

font = FontProperties()
font.set_family( 'serif' )
font.set_name( 'Times New Roman' )
font.set_size( 15 )

anno_font = FontProperties()
anno_font.set_family( 'serif' )
anno_font.set_name( 'Times New Roman' )
anno_font.set_size( 10 )

#-------------------------------------------------------------------------
# interp_value
#-------------------------------------------------------------------------

def interp_value( val, x, y ):
  fn = interp1d( x, y, kind='linear' )
  return fn( val )

#-------------------------------------------------------------------------
# extrap_value
#-------------------------------------------------------------------------

def extrap_value( val, x, y ):
  fn = np.polyfit( x, y, 1 )
  return np.polyval( fn, val )

#-------------------------------------------------------------------------
# calc_ser_lat
#-------------------------------------------------------------------------

def calc_ser_lat( msg_size, channel_nbits ):
  ser_lat = msg_size // channel_nbits
  if msg_size - ser_lat*channel_nbits > 0:
    ser_lat += 1
  return ser_lat


#-------------------------------------------------------------------------
# constatns
#-------------------------------------------------------------------------

bw_factor = {
  'mesh-c1': 32,
  'mesh-c4': 16,
  'mesh-c8': 8,
  'mesh-c1e1': 96,
  'mesh-c4e1': 48,
  'mesh-c8e1': 24,
  'mesh-c1e2': 128,
  'mesh-c4e2': 64,
  'mesh-c8e2': 32,

  'torus-c1': 64,
  'torus-c4': 32,
  'torus-c8': 16,
  'torus-c1eN': 96,
  'torus-c4eN': 48,
  'torus-c8eN': 24,
  'mesh-c1e1q0': 32,
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

def assign_style( name ):
  lst = name.split( '-' )
  # skip factor
  marker = 'x' if lst[0]    == 'torus' else \
           's' if lst[1].endswith('e2') else \
           '^' if lst[1].endswith('e1') else \
           'o'

  line   = '-'  if lst[0]== 'mesh' else \
           '-'
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

def mk_plot( norm_bws=[ 2048, 4096 ] ):
  msg_sizes = [ 64, 512 ]
  bc_lst    = [ 32, 64, 128, 256, 512 ]

  ncols = len( norm_bws )
  nrows = len( msg_sizes )
  fig = plt.figure( figsize=(4*ncols, 4*nrows) )
  axes = [ [ None for _ in range( ncols ) ] for _ in range( nrows )]

  # font = FontProperties()
  # font.set_family( 'serif' )
  # font.set_name( 'Times New Roman' )
  # font.set_size( 13 )

  ylimit = [
    [ 25, 25, 25 ],
    [ 40, 40, 40 ],
  ]

  xlimit = [
    [ 0.10, 0.15 ],
    [ 0.2,  0.3 ],
  ]

  xticks = [
    [ [0, 0.05, 0.10             ], [ 0, 0.05, 0.10, 0.15] ],
    [ [0, 0.05, 0.10, 0.15, 0.20 ], [ 0, 0.1,  0.2,  0.3] ],
  ]

  xticklabels = [ [ [ f'{int(x*100)}' if x>0 else f'0' for x in lst ] for lst in row ] for row in xticks ]

  offsets = [
    [ { 'mesh-c4e2' : (-0.005, -0.8) }, { } ],
    [ { 'torus-c8': (-0.002, -1.8) }, { 'torus-c4': (-0.03, -2), 'mesh-c4e1': (0,-2), 'mesh-c8e1' : (0,-2), 'torus-c8':(-0.035,-0.5) } ],
  ]
  for r, msg_size in enumerate( msg_sizes ):

    # mesh-c1s1
    mc1s1  = []
    for bc in bc_lst:
      ser_lat  = msg_size // bc
      h_lat, _ = mesh_cxs1_lat( 16, 16, 1, ser_lat, 1 )
      tile_w, tile_h = tile_dimensions[ 'c1' ]
      area     = mesh_c1s1_area( bc, tile_h, tile_w )
      mc1s1.append(
        Entry(
          name  = 'mesh-c1',
          bw    = bc * bw_factor[ 'mesh-c1' ],
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
          name  = 'mesh-c4',
          bw    = bc * bw_factor[ 'mesh-c4' ],
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
          name  = 'mesh-c8',
          bw    = bc * bw_factor[ 'mesh-c8' ],
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
          name  = 'mesh-c1e1',
          bw    = bc * bw_factor[ 'mesh-c1e1' ],
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
          name  = 'mesh-c4e1',
          bw    = bc * bw_factor[ 'mesh-c4e1' ],
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
          name  = 'mesh-c8e1',
          bw    = bc * bw_factor[ 'mesh-c8e1' ],
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
          name  = 'mesh-c1e2',
          bw    = bc * bw_factor[ 'mesh-c1e2' ],
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
          name  = 'mesh-c4e2',
          bw    = bc * bw_factor[ 'mesh-c4e2' ],
          chnl  = bc,
          s_lat = ser_lat,
          h_lat = h_lat,
          area  = area,
      ))

    # mesh-c8s3
    mc8s3  = []
    for bc in bc_lst:
      ser_lat  = msg_size // bc
      h_lat, _ = mesh_cxs3_lat( 4, 8, 8, 2, ser_lat, 1 )
      tile_w, tile_h = tile_dimensions[ 'c8' ]
      area     = mesh_c8s3_area( bc, tile_h, tile_w )
      mc8s3.append(
        Entry(
          name  = 'mesh-c8e2',
          bw    = bc * bw_factor[ 'mesh-c8e2' ],
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
          name  = 'torus-c1',
          bw    = bc * bw_factor[ 'torus-c1' ],
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
          name  = 'torus-c4',
          bw    = bc * bw_factor[ 'torus-c4' ],
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
          name  = 'torus-c8',
          bw    = bc * bw_factor[ 'torus-c8' ],
          chnl  = bc,
          s_lat = ser_lat,
          h_lat = h_lat,
          area  = area,
      ))

    mc1s1q0 = []
    for bc in bc_lst:
      if bc <= 64:
        ser_lat  = msg_size // bc
        h_lat, _ = mesh_cxs1_lat( 16, 16, 1, ser_lat, 0 )
        tile_w, tile_h = tile_dimensions[ 'c1' ]
        area     = mesh_c1s1_area( bc, tile_h, tile_w )
        mc1s1q0.append(
          Entry(
            name  = 'mesh-c1e1q0',
            bw    = bc * bw_factor[ 'mesh-c1' ],
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



    #=======================================================================
    # plotting
    #=======================================================================
    # TODO: marker and line styles


      # if t == 'mesh':
      # else:
      #   return 'lightcoral' if c == 1 else \
      #          'firebrick' if c == 4 else \
      #          'darkred'

    data_sets = [
      mc1s1, mc4s1, mc8s1, # mc1s1q0,
      mc1s2, mc4s2, mc8s2,
      mc1s3, mc4s3, mc8s3,
      tc1s1, tc4s1, tc8s1,

      # tc1sN, tc4sN, tc8sN,
    ]

    # bw vs lat under area constraints
    for c, norm_bw in enumerate( norm_bws ):
      idx = r * ncols + c + 1
      axes[r][c] = fig.add_subplot( nrows, ncols, idx )

      for data in data_sets:

        # lat = [ x.h_lat for x in data if x.chnl <= msg_sie ]
        h_lat = data[0].h_lat # path latency is the same across different bw
        bw    = [ x.bw   for x in data if x.chnl <= msg_size ]
        chnl  = [ x.chnl for x in data if x.chnl <= msg_size ]
        area  = [ x.area for x in data if x.chnl <= msg_size ]

        if bw[-1]  < norm_bw:
          print( f'{data[0].name} cannot reach bandwidth of {norm_bw}' )
          continue

        elif bw[0] > norm_bw:
          print( f'{data[0].name} has minimum bandwidth of {bw[0]} which exceeds {norm_bw}' )
          # Scales down the bw
          # norm_chnl = extrap_value( norm_bw, bw[0:1], chnl[0:1] )
          norm_chnl = norm_bw/bw_factor[data[0].name]
          norm_lat  = h_lat + calc_ser_lat( msg_size, norm_chnl )
          norm_area = extrap_value( norm_bw, bw[0:1], area[0:1] )

        else:

          # norm_chnl = interp_value( norm_bw, bw, chnl )
          norm_chnl = norm_bw/bw_factor[data[0].name]
          norm_lat  = h_lat + calc_ser_lat( msg_size, norm_chnl )
          norm_area = interp_value( norm_bw, bw, area )

        print( f'[{norm_bw}]: processing {data[0].name}... normalized channel: {norm_chnl}b, area {norm_area}' )

        style = assign_style( data[0].name )
        color = assign_color( data[0].name )

        # if len( lat ) > 0:
        #   optimal_bw  = [ bw[-1] ]
        #   optimal_lat = [lat[-1] ]
        if data[0].name == 'mesh-c1e1q0':
          facecolor = 'none'
        else:
          facecolor = color

        axes[r][c].plot( [norm_area], [norm_lat], style, color=color, label=data[0].name, markersize=6, markerfacecolor=facecolor, linewidth=0 )

        if data[0].name in offsets[r][c]:
          x_offset, y_offset = offsets[r][c][data[0].name]
        else:
          x_offset = y_offset = 0

        axes[r][c].annotate( f'{int(norm_chnl)}', (norm_area+x_offset, norm_lat+y_offset), fontproperties=anno_font )

        axes[r][c].spines['top'  ].set_visible( False )
        axes[r][c].spines['right'].set_visible( False )
        axes[r][c].set_ylim( bottom=0, top=ylimit[r][c]*1.2)
        # axes[r][c].set_xlim( 0, xlimit[r][c]*1.1 )
        axes[r][c].set_xlim( 0, xlimit[r][c]*1.2 )

        axes[r][c].grid( color='grey', linestyle='--' )
        axes[r][c].set_ylabel( 'zero load latency (cycles)', fontproperties=font )
        axes[r][c].set_xlabel( 'area (%)', fontproperties=font )

        axes[r][c].set_xticks( xticks[r][c] )
        axes[r][c].set_xticklabels( xticklabels[r][c], fontproperties=font)
        # axes[r][c].get_xticklabels()[0].set_text( '0' )
        for i, tick in enumerate( axes[r][c].get_xticklabels() ):
          tick.set_fontproperties( font )

        for tick in axes[r][c].get_yticklabels():
          tick.set_fontproperties( font )
  # axes[0][0].set_ylabel( 'zero load latency', position=(1, -0.25) ) # TODO: font

  # for c in range( ncols ):
    # axes[0][c].set_title( f'bisection bandwidth {norm_bws[c]}b' )

  # for r in range( nrows ):
  #   axes[r][0].set_xticks( [ 1024, 2048, 3072, 4096, 5120 ] )
  #   axes[r][1].set_xticks( [ 2048, 4096, 6144, 8192, 10240, 12288 ] )

  # axes[0][0].set_xticklabels( [] )
  # axes[0][1].set_xticklabels( [] )
  # axes[1][0].set_xticklabels( [ '1K', '2K', '3K', '4K', '5K' ] )
  # axes[1][1].set_xticklabels( [ '2K', '4K', '6K', '8K', '10K', '12K' ] )

  axes[0][0].text( 0.5, -0.325, r'(a) B = 2K, M = 64',
                   horizontalalignment='center', multialignment='left', fontproperties=font,
                   transform=axes[0][0].transAxes )


  axes[0][1].text( 0.5, -0.325, r'(b) B = 4K, M = 64',
                   horizontalalignment='center', multialignment='left', fontproperties=font,
                   transform=axes[0][1].transAxes )

  # Move second row down a little
  bbox = list( axes[1][0].get_position().bounds )
  bbox[1] -= 0.08
  axes[1][0].set_position(bbox)

  bbox = list( axes[1][1].get_position().bounds )
  bbox[1] -= 0.08
  axes[1][1].set_position(bbox)

  axes[1][0].text( 0.5, -0.325, r'(c) B = 2K, M = 512',
                   horizontalalignment='center', multialignment='left', fontproperties=font,
                   transform=axes[1][0].transAxes )


  axes[1][1].text( 0.5, -0.325, r'(d) B = 4K, M = 512',
                   horizontalalignment='center', multialignment='left', fontproperties=font,
                   transform=axes[1][1].transAxes )

  # plt.legend( bbox_to_anchor=( 0, -0.375, 0.5, 0.5), ncol=4, prop=font, frameon=False, mode='expand' )
  # plt.legend(  ncol=4, prop=font, frameon=False, mode='expand' )
  plt.legend( bbox_to_anchor=(1.0, -0.375 ), ncol=4, prop=font, frameon=False )

  # plt.title( f'msg size: {msg_size}')
  plt.savefig( f'norm-lat-area.pdf', bbox_inches='tight' )


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