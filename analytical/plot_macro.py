import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from dataclasses import dataclass
import numpy as np
from ubmark_data import *
# params = {'text.latex.preamble': [r'\usepackage{siunitx}',
#     r'\usepackage{sfmath}', r'\sisetup{detect-family = true}',
#     r'\usepackage{amsmath}']}
# plt.rcParams.update(params)

font = FontProperties()
font.set_family( 'serif' )
font.set_name( 'Times New Roman' )
font.set_size( 13 )

bw_factor = {
  'mesh-c1': 32,
  'mesh-c1q0': 32,
  'mesh-c4': 16,
  'mesh-c8': 8,
  'mesh-c1r2': 96,
  'mesh-c4r2': 48,
  'mesh-c8r2': 24,
  'mesh-c1r3': 128,
  'mesh-c4r3': 64,
  'mesh-c8r3': 32,

  'torus-c1': 64,
  'torus-c4': 32,
  'torus-c8': 16,
  'torus-c1eN': 96,
  'torus-c4eN': 48,
  'torus-c8eN': 24,
}

@dataclass
class Design:
  # name  : str
  chnl  : int
  area  : float
  h_lat : float

macros = {

  'mesh-c1'   : [ Design( 32, 0.04979591837, 21.25 ),
                  Design( 64, 0.06742857143, 21.25 ),
                  Design( 128, 0.1632653061, 21.25 ),
                  Design( 256, 0.3534693878, 21.25 ) ],

  'mesh-c1q0' : [ Design( 32, 0.07869387755, 10.625 ),
                  Design( 64, 0.1379591837,  10.625 ) ],

  'mesh-c4'   : [ Design( 32,  0.0266466504,  10.5 ),
                  Design( 64,  0.04597485457, 10.5 ),
                  Design( 128, 0.1020829424,  10.5 ) ],

  'mesh-c4r2' : [ Design( 32 , 0.06458997936, 6.25 ),
                  Design( 64 , 0.107524864, 6.25 ),
                  Design( 128, 0.2253706136,  6.25 ) ],

  'torus-c1'  : [ Design( 32, 0.08620408163, 8 ),
                  Design( 64, 0.1771428571,  8 ),
                  Design( 128, 0.3755102041, 8 ) ],

}
K = 1024

#-------------------------------------------------------------------------
# helper
#-------------------------------------------------------------------------

def assign_style( name ):
  lst = name.split( '-' )
  # skip factor
  marker = 'x' if lst[0]    == 'torus' else \
           's' if lst[1].endswith('r3') else \
           '^' if lst[1].endswith('r2') else \
           'o'

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
# main
#-------------------------------------------------------------------------

if __name__ == '__main__':
  fig = plt.figure( figsize=(4.5*3, 4) )

  #-----------------------------------------------------------------------
  # bw vs area
  #-----------------------------------------------------------------------

  ax0 = fig.add_subplot(1, 3, 1)
  for name, designs in macros.items():
    bw    = [ x.chnl * bw_factor[name] for x in designs ]
    area  = [ x.area for x in designs ]

    style = assign_style( name )
    color = assign_color( name )
    if name.endswith( 'q0' ):
      facecolor = 'none'
    else:
      facecolor = color

    ax0.plot( area, bw, style, color=color, label=name, markersize=6, markerfacecolor=facecolor, linewidth=1 )

  xticks = [ 0, 0.1, 0.2, 0.3 ]
  yticks = [ x*K for x in range(9) ]

  xticklabels = [ f'{int(x*100)}' for x in xticks ]
  yticklabels = [ f'{y//K}' for y in yticks ]
  ax0.set_xlim(0, 0.38)
  ax0.set_ylim(0, 8.2*K)
  ax0.spines['top'  ].set_visible( False )
  ax0.spines['right'].set_visible( False )
  ax0.grid( color='grey', linestyle='--' )
  ax0.set_ylabel( r'Bisection Bandwidth (Kb/cycle)', fontproperties=font )
  ax0.set_xlabel( r'Area Overhead (%)', fontproperties=font )
  ax0.set_xticks( xticks )
  ax0.set_yticks( yticks )
  ax0.set_xticklabels( xticklabels )
  ax0.set_yticklabels( yticklabels )

  ax0.text( 0.5, -0.22, '(a)',
            horizontalalignment='center', multialignment='left', fontproperties=font,
            transform=ax0.transAxes )
  for tick in ax0.get_xticklabels():
    tick.set_fontproperties( font )
  for tick in ax0.get_yticklabels():
    tick.set_fontproperties( font )

  #-----------------------------------------------------------------------
  # lat vs area small
  #-----------------------------------------------------------------------

  msg_size = 64
  ax1 = fig.add_subplot(1, 3, 2)
  for name, designs in macros.items():
    lat   = [ x.h_lat + msg_size//x.chnl for x in designs if x.chnl <= msg_size ]
    area  = [ x.area for x in designs if x.chnl <= msg_size]

    style = assign_style( name )
    color = assign_color( name )
    if name.endswith( 'q0' ):
      facecolor = 'none'
    else:
      facecolor = color

    ax1.plot( area, lat, style, color=color, label=name, markersize=6, markerfacecolor=facecolor, linewidth=1 )

  xticks = [ 0, 0.05, 0.1, 0.15, 0.2 ]
  yticks = [ 0, 5, 10, 15, 20, 25 ]

  xticklabels = [ f'{int(x*100)}' for x in xticks ]
  yticklabels = [ f'{y}' for y in yticks ]
  ax1.set_xlim(0, 0.21)
  ax1.set_ylim(0, 26)
  ax1.spines['top'  ].set_visible( False )
  ax1.spines['right'].set_visible( False )
  ax1.grid( color='grey', linestyle='--' )
  ax1.set_ylabel( r'Zero Load Latency (cycles)', fontproperties=font )
  ax1.set_xlabel( r'Area Overhead (%)', fontproperties=font )
  ax1.set_xticks( xticks )
  ax1.set_yticks( yticks )
  ax1.set_xticklabels( xticklabels )
  ax1.set_yticklabels( yticklabels )

  ax1.text( 0.5, -0.22, '(b) M = 64',
            horizontalalignment='center', multialignment='left', fontproperties=font,
            transform=ax1.transAxes )
  for tick in ax1.get_xticklabels():
    tick.set_fontproperties( font )
  for tick in ax1.get_yticklabels():
    tick.set_fontproperties( font )

  #-----------------------------------------------------------------------
  # lat vs area large
  #-----------------------------------------------------------------------

  msg_size = 256
  ax2 = fig.add_subplot(1, 3, 3)
  for name, designs in macros.items():
    lat   = [ x.h_lat + msg_size//x.chnl for x in designs if x.chnl <= msg_size ]
    area  = [ x.area for x in designs if x.chnl <= msg_size]

    style = assign_style( name )
    color = assign_color( name )
    if name.endswith( 'q0' ):
      facecolor = 'none'
    else:
      facecolor = color

    ax2.plot( area, lat, style, color=color, label=name, markersize=6, markerfacecolor=facecolor, linewidth=1 )

  xticks = [ 0, 0.1, 0.2, 0.3, 0.4 ]
  yticks = [ 0, 10, 20, 30 ]

  xticklabels = [ f'{int(x*100)}' for x in xticks ]
  yticklabels = [ f'{y}' for y in yticks ]
  ax2.set_xlim(0, 0.42)
  ax2.set_ylim(0, 32)
  ax2.spines['top'  ].set_visible( False )
  ax2.spines['right'].set_visible( False )
  ax2.grid( color='grey', linestyle='--' )
  ax2.set_ylabel( r'Zero Load Latency (cycles)', fontproperties=font )
  ax2.set_xlabel( r'Area Overhead (%)', fontproperties=font )
  ax2.set_xticks( xticks )
  ax2.set_yticks( yticks )
  ax2.set_xticklabels( xticklabels )
  ax2.set_yticklabels( yticklabels )

  ax2.text( 0.5, -0.22, '(b) M = 256',
            horizontalalignment='center', multialignment='left', fontproperties=font,
            transform=ax2.transAxes )
  for tick in ax2.get_xticklabels():
    tick.set_fontproperties( font )
  for tick in ax2.get_yticklabels():
    tick.set_fontproperties( font )

  # plt.tight_layout()
  plt.legend( bbox_to_anchor=(0.5, -0.2 ), ncol=5, prop=font, frameon=False )

  plt.savefig( f'macro-plots.pdf', bbox_inches='tight', pad_inches=0 )