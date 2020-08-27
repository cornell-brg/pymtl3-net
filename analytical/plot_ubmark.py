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
font.set_size( 12.5 )

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
  fig = plt.figure( figsize=(4.5, 2.5) )
  ax0 = fig.add_subplot(2, 1, 1)
  ax0.plot( distance, reg2reg, '-o', markersize=6, linewidth=1 )
  ax0.set_xlim(0, 660)
  ax0.set_ylim(0, 360)
  ax0.spines['top'  ].set_visible( False )
  ax0.spines['right'].set_visible( False )
  ax0.grid( color='grey', linestyle='--' )
  ax0.set_ylabel( r'Cycle time (ps)', fontproperties=font )
  ax0.set_xlabel( r'Distance (um)', fontproperties=font )
  ax0.set_xticks([0, 100, 200, 300, 400, 500, 600])

  ax0.text( 0.5, -0.5, '(a) Channel Latency Results',
            horizontalalignment='center', multialignment='left', fontproperties=font,
            transform=ax0.transAxes )
  for tick in ax0.get_xticklabels():
    tick.set_fontproperties( font )
  for tick in ax0.get_yticklabels():
    tick.set_fontproperties( font )


  ax1 = fig.add_subplot(2, 1, 2)
  for nbits in [256, 32, 64, 128, ]:
    radix = [ x.radix for x in db if x.channel_nbits == nbits ]
    area  = [ x.area for x in db  if x.channel_nbits == nbits ]
    ax1.plot( radix, area, '-o', markersize=6, linewidth=1, label=f'{nbits}b' )

  ax1.spines['top'  ].set_visible( False )
  ax1.spines['right'].set_visible( False )
  ax1.grid( color='grey', linestyle='--' )
  # ax1.legend(bbox_to_anchor=(0.9, -0.3 ), frameon=False, ncol=2, prop=font)
  ax1.legend(frameon=False, ncol=2, prop=font)
  ax1.set_yticks([0, 4000, 8000, 12000])
  ax1.set_yticklabels(['0', '4k', '8k', '12k'], fontproperties=font)
  ax1.set_ylim(0, 13000)
  ax1.set_xlabel( r'Radix', fontproperties=font )
  ax1.set_ylabel( r'Area (sq. um)', fontproperties=font )
  for tick in ax1.get_xticklabels():
    tick.set_fontproperties( font )

  bbox = list( ax1.get_position().bounds )
  bbox[1] -= 0.4
  ax1.set_position(bbox)
  ax1.text( 0.5, -0.5, '(b) Router Area Results',
            horizontalalignment='center', multialignment='left', fontproperties=font,
            transform=ax1.transAxes )
  # plt.tight_layout()
  plt.savefig( f'ubmark.pdf', bbox_inches='tight', pad_inches=0 )