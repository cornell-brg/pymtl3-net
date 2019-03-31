#=========================================================================
# Packet.py
#=========================================================================
# A simple Packet format for testing
#
# Author : Yanghui Ou, Cheng Tan
#   Date : Mar 26, 2019

from pymtl import *

import py

#-------------------------------------------------------------------------
# Static Packet type
#-------------------------------------------------------------------------

class Packet( object ):

  def __init__( s ):
    
    s.src_x   = Bits4 ( 0 )
    s.src_y   = Bits4 ( 0 ) 
    s.dst_x   = Bits4 ( 0 ) 
    s.dst_y   = Bits4 ( 0 ) 
    s.opaque  = Bits4 ( 0 ) 
    s.payload = Bits16( 0 )

  def __str__( s ):
    return "({},{})>({},{}):{}:{}".format(
      s.src_x, s.src_y, s.dst_x, s.dst_y, s.opaque, s.payload ) 

def mk_pkt( src_x, src_y, dst_x, dst_y, opaque, payload ):
  pkt = Packet()
  pkt.src_x   = src_x
  pkt.src_y   = src_y
  pkt.dst_x   = dst_x
  pkt.dst_y   = dst_y
  pkt.opaque  = opaque
  pkt.payload = payload
  return pkt

# TODO: flitisize packet into multiple flits 
#def flitisize():
#  pass

#-------------------------------------------------------------------------
# Dynamically generated Packet type
#-------------------------------------------------------------------------

_packet_dic = dict()
_packet_template = """
class Packet_{src_pos}_{dst_pos}_{opaque_nbits}_{payload_nbits}( object ):

  def __init__( s, src=0, dst=0, opaque=0, payload=0 ):
    pass

  def __str__( s ):
    pass
"""
