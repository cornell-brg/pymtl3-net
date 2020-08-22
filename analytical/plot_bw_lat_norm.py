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
import numpy as np
from scipy.interpolate import interp1d
from matplotlib.font_manager import FontProperties

#-------------------------------------------------------------------------
# font
#-------------------------------------------------------------------------

font = FontProperties()
font.set_family( 'serif' )
font.set_name( 'Times New Roman' )
font.set_size( 15 )

anno_font = FontProperties()
anno_font.set_family( 'serif' )
anno_font.set_name( 'Times New Roman' )
anno_font.set_size( 10 )

K = 1024

#-------------------------------------------------------------------------
# interp_point
#-------------------------------------------------------------------------

def interp_value( val, x, y ):
  fn = interp1d( [0] + x, [0] + y, kind='linear' )
  return fn( val )

#-------------------------------------------------------------------------
# extrap_value
#-------------------------------------------------------------------------

def extrap_value( val, x, y ):
  fn = np.polyfit( [0] + x, [0] + y, 1 )
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

def mk_plot( area_constraints=[ 0.1, 0.25 ] ):
  msg_sizes = [ 64, 512 ]
  bc_lst    = [ 32, 64, 128, 256, 512 ]

  ncols = len( area_constraints )
  nrows = len( msg_sizes )
  fig = plt.figure( figsize=(4*ncols, 4*nrows) )
  axes = [ [ None for _ in range( ncols ) ] for _ in range( nrows )]

  # font = FontProperties()
  # font.set_family( 'serif' )
  # font.set_name( 'Times New Roman' )
  # font.set_size( 13 )

  limit = [
    [ 25, 25 ],
    [ 40, 40 ],
  ]

  xlimit = [
    [ 4*K, 8*K ],
    [ 4*K, 12*K ],
  ]

  xticks = [
    [ 0, 1*K, 2*K, 3*K, 4*K ], [ 0, 2*K, 4*K, 6*K, 8*K ],
    [ 0, 1*K, 2*K, 3*K, 4*K ], [ 0, 4*K, 8*K, 12*K ],
  ]

  xticklabels = [ [ f'{x//K}Kb' if x>0 else '0' for x in rows ] for rows in xticks ]

  offsets = [
    [ {}, {} ],
    [ { 'mesh-c8': (-0.2*K, 0), 'mesh-c4': (-0.2*K, 0), 'torus-c8': (0, -0.8) }, { 'mesh-c8': (-0.4*K, 0), 'mesh-c1e2': (0.2*K, -0.5), 'torus-c8': (-0.65*K, 0.5), 'mesh-c8e1':(0, -1.5), 'mesh-c4e1':(-0.6*K, -1), 'torus-c4':(0,-1.5) } ],
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
    for c, A_constraint in enumerate( area_constraints ):
      idx = r * ncols + c + 1
      axes[r][c] = fig.add_subplot( nrows, ncols, idx )

      for data in data_sets:

        # lat = [ x.h_lat for x in data if x.chnl <= msg_sie ]
        h_lat = data[0].h_lat # path latency is the same across different bw
        bw    = [ x.bw   for x in data if x.chnl <= msg_size ]
        chnl  = [ x.chnl for x in data if x.chnl <= msg_size ]
        area  = [ x.area for x in data if x.chnl <= msg_size ]

        if area[-1]  <= A_constraint*1.05:
          norm_area = area[-1]
          norm_chnl = interp_value( norm_area, area, chnl )
          # norm_bw   = interp_value( norm_area, area, bw )
          norm_bw   = norm_chnl * bw_factor[ data[0].name ]
          norm_lat  = h_lat + calc_ser_lat( msg_size, norm_chnl )
        elif area[0] > A_constraint*1.05:
          print( f'scaling down {data[0].name} which is too large for {A_constraint}' )
          norm_area = A_constraint
          # norm_chnl = extrap_value( norm_area, area, chnl )
          # norm_bw   = extrap_value( norm_area, area, bw )
          norm_chnl = interp_value( norm_area, area, chnl )
          norm_bw   = norm_chnl * bw_factor[ data[0].name ]
          # norm_bw   = interp_value( norm_area, area, bw )
          norm_lat  = h_lat + calc_ser_lat( msg_size, norm_chnl )
        else:
          norm_area = A_constraint*1.05
          norm_chnl = interp_value( norm_area, area, chnl )
          norm_bw   = norm_chnl * bw_factor[ data[0].name ]
          # norm_bw   = interp_value( norm_area, area, bw )
          norm_lat  = h_lat + calc_ser_lat( msg_size, norm_chnl )

        print( f'[{A_constraint}]: processing {data[0].name}... normalized channel: {norm_chnl}b, bandwidth {norm_bw}' )

        style = assign_style( data[0].name )
        color = assign_color( data[0].name )

        # if len( lat ) > 0:
        #   optimal_bw  = [ bw[-1] ]
        #   optimal_lat = [lat[-1] ]

        if data[0].name == 'mesh-c1e1q0':
          facecolor = 'none'
        else:
          facecolor = color

        axes[r][c].plot( [norm_bw], [norm_lat], style, color=color, label=data[0].name, markersize=6, markerfacecolor=facecolor, linewidth=0 )


        # Annotate
        if data[0].name in offsets[r][c]:
          x_offset, y_offset = offsets[r][c][data[0].name]
        else:
          x_offset = y_offset = 0

        axes[r][c].annotate( f'{int(norm_chnl)}', (norm_bw+x_offset, norm_lat+y_offset), fontproperties=anno_font )

        axes[r][c].spines['top'  ].set_visible( False )
        axes[r][c].spines['right'].set_visible( False )
        axes[r][c].set_ylim( top=limit[r][c]*1.2, bottom=0 )
        axes[r][c].set_xlim( 0, xlimit[r][c]*1.2 )
        axes[r][c].set_xticklabels( xticklabels[c+r*ncols] )
        axes[r][c].set_ylabel( 'zero load latency', fontproperties=font )
        axes[r][c].set_xlabel( 'bisection bandwidth', fontproperties=font )
        # axes[r][c].grid()
        axes[r][c].grid( color='grey', linestyle='--' )
        for tick in axes[r][c].get_xticklabels():
          tick.set_fontproperties( font )
        for tick in axes[r][c].get_yticklabels():
          tick.set_fontproperties( font )

  # axes[0][0].set_ylabel( 'zero load latency', position=(1, -0.25) ) # TODO: font
  # axes[1][0].set_xlabel( 'bisection bandwidth', position=(1.1, 1) )

  # for c in range( ncols ):
  # axes[0][0].set_title( f'10% area' )
  # axes[0][1].set_title( f'30% area' )

  # axes[0][0].set_ylabel( f'64b message size' )
  # axes[1][0].set_ylabel( f'512b message size' )

  # for r in range( nrows ):
  #   axes[r][0].set_xticks( [ 1024, 2048, 3072, 4096, 5120 ] )
  #   axes[r][1].set_xticks( [ 2048, 4096, 6144, 8192, 10240, 12288 ] )

  # axes[0][0].set_xticklabels( [] )
  # axes[0][1].set_xticklabels( [] )
  # axes[1][0].set_xticklabels( [ '1K', '2K', '3K', '4K', '5K' ] )
  # axes[1][1].set_xticklabels( [ '2K', '4K', '6K', '8K', '10K', '12K' ] )

  axes[0][0].text( 0.5, -0.325, '(a) A = 10%, M = 64',
                   horizontalalignment='center', multialignment='left', fontproperties=font,
                   transform=axes[0][0].transAxes )


  axes[0][1].text( 0.5, -0.325, '(b) A = 25%, M = 64',
                   horizontalalignment='center', multialignment='left', fontproperties=font,
                   transform=axes[0][1].transAxes )

  # Move second row down a little
  bbox = list( axes[1][0].get_position().bounds )
  bbox[1] -= 0.08
  axes[1][0].set_position(bbox)

  bbox = list( axes[1][1].get_position().bounds )
  bbox[1] -= 0.08
  axes[1][1].set_position(bbox)

  axes[1][0].text( 0.5, -0.325, f'(c) A = 10%, M = 512',
                   horizontalalignment='center', multialignment='left', fontproperties=font,
                   transform=axes[1][0].transAxes )


  axes[1][1].text( 0.5, -0.325, f'(d) A = 25%, M = 512',
                   horizontalalignment='center', multialignment='left', fontproperties=font,
                   transform=axes[1][1].transAxes )

  plt.legend( bbox_to_anchor=(1.0, -0.375 ), ncol=4, prop=font, frameon=False )
  # plt.title( f'msg size: {msg_size}')
  plt.savefig( f'norm-lat-bw.pdf', bbox_inches='tight' )


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