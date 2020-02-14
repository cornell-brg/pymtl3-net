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

  dst = 0
  for packets in src_pkts:
    for pkt in packets:
      # TODO: change vc_id?
      if hasattr(pkt, 'fl_type'):
        if pkt.fl_type == 0:
          dst = pkt.dst
      else:
        dst = pkt.dst
      dst_pkts[ dst ].append( pkt )
  return dst_pkts

# class RingNetworkFL( Component ):
#   def construct( s, nterminals ):
#     s.recv = [ RecvIfcFL( method=s.recv_ ) for _ in range( nterminals ) ]
#     s.send = [ SendIfcFL() for _ in range( nterminals ) ]
# 
#     s.out_q = [ QueueFL() for _ in range( nterminals ) ]
# 
#     for i in range( nterminals ):
#       s.connect( s.out_q.send, s.send )
# 
#   def recv_( s, pkt ):
#     s.out_q[ int(pkt.dst) ].enq( pkt )
