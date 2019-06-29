"""
==========================================================================
RingNetworkFL
==========================================================================
Functional level of a ring network.

Author : Yanghui Ou
  Date : June 28, 2019
"""

from pymtl3 import *

#-------------------------------------------------------------------------
# ringnet_fl
#-------------------------------------------------------------------------
# [src_pkts] is a list of lists of packets, where each list of packets
# represents traffic from a certain terminal. The FL model returns
# [dst_pkts], which is also a list of lists of packets, where each list of
# packets represents the output packets of each terminal.

def ringnet_fl( src_pkts ):
  nterminals = len( src_pkts )
  dst_pkts = [ [] for _ in range( nterminals ) ]

  for packets in src_pkts:
    for pkt in packets:
      # TODO: change vc_id?
      dst_pkts[ int(pkt.dst) ].append( pkt )
  return dst_pkts
