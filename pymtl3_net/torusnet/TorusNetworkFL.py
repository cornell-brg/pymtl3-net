"""
==========================================================================
TorusNetworkFL
==========================================================================
Functional level implementation of a torus network.

Author : Yanghui Ou
  Date : July 1, 2019
"""

from pymtl3 import *

#-------------------------------------------------------------------------
# torusnet_fl
#-------------------------------------------------------------------------
# [src_pkts] is a list of lists of packets, where each list of packets
# represents traffic from a certain terminal. The FL model returns
# [dst_pkts], which is also a list of lists of packets, where each list of
# packets represents the output packets of each terminal.

def torusnet_fl( ncols, nrows, src_pkts ):
  nterminals = ncols * nrows
  assert len( src_pkts ) == nterminals

  dst_pkts = [ [] for _ in range( nterminals ) ]

  for packets in src_pkts:
    for pkt in packets:
      # TODO: change vc_id?
      dst_id = int(pkt.dst_x) + int(pkt.dst_y) * ncols
      dst_pkts[ dst_id ].append( pkt )
  return dst_pkts
