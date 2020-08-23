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
font.set_size( 15 )

def extrap_value( val, x, y ):
  fn = np.polyfit( x, y, 2 )
  return np.polyval( fn, val )

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

distance = [ 100, 200, 300, 400, 500, 600 ]
reg2reg  = [ 100, 175, 200, 225, 270, 325 ]

router_db = {
  '950ps' : db_950,
  '850ps' : db_850,
  '750ps' : db_750,
  '650ps' : db_650,
}

db= db_850

if __name__ == '__main__':
  fig = plt.figure( figsize=(3.5, 3.5) )
  ax0 = fig.add_subplot(2, 1, 1)
  ax0.plot( distance, reg2reg, '-o', markersize=6, linewidth=1 )
  ax0.set_xlim(0, 660)
  ax0.set_ylim(0, 360)
  ax0.spines['top'  ].set_visible( False )
  ax0.spines['right'].set_visible( False )
  ax0.grid( color='grey', linestyle='--' )
  ax0.set_ylabel( r'cycle time (ps)', fontproperties=font )
  ax0.set_xlabel( r'distance ($\mu$m)', fontproperties=font )
  ax0.text( 0.5, -0.475, '(a) channel latency model',
            horizontalalignment='center', multialignment='left', fontproperties=font,
            transform=ax0.transAxes )


  ax1 = fig.add_subplot(2, 1, 2)
  for nbits in [32, 64, 128, 256, 512]:
    radix = [ x.radix for x in db if x.channel_nbits == nbits ]
    area  = [ x.area for x in db  if x.channel_nbits == nbits ]
    ax1.plot( radix, area, '-o', markersize=6, linewidth=1, label=f'{nbits}b' )

  ax1.spines['top'  ].set_visible( False )
  ax1.spines['right'].set_visible( False )
  ax1.grid( color='grey', linestyle='--' )
  ax1.legend(loc='best', frameon=False)
  ax1.set_xlabel( r'radix', fontproperties=font )
  ax1.set_ylabel( r'area ($\mu$m$^2$)', fontproperties=font )

  bbox = list( ax1.get_position().bounds )
  bbox[1] -= 0.15
  ax1.set_position(bbox)
  ax1.text( 0.5, -0.475, '(b) router area model',
            horizontalalignment='center', multialignment='left', fontproperties=font,
            transform=ax1.transAxes )


  plt.savefig( f'ubmark.pdf', bbox_inches='tight' )