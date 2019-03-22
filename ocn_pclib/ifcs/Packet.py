#=========================================================================
# Packet.py
#=========================================================================
# A simple Packet format for testing
#
# Author : Cheng Tan
#   Date : Mar 3, 2019

from pymtl import *

class Packet( object ):
  def __init__(s):
    
    s.src_x   = Bits4 ( 0 )
    s.src_y   = Bits4 ( 0 ) 
    s.dst_x   = Bits4 ( 0 ) 
    s.dst_y   = Bits4 ( 0 ) 
    s.opaque  = Bits4 ( 0 ) 
    s.payload = Bits16( 0 )

def mk_pkt( src_x, src_y, dst_x, dst_y, opaque, payload ):
  pkt = Packet()
  pkt.src_x   = src_x
  pkt.src_y   = src_y
  pkt.dst_x   = dst_x
  pkt.dst_y   = dst_y
  pkt.opaque  = opaque
  pkt.payload = payload
  return pkt
