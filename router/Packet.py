#=========================================================================
# Packet.py
#=========================================================================
# A simple Packet format for testing
#
# Author : Cheng Tan
#   Date : Mar 3, 2019

from pymtl import *

class Packet( RTLComponent ):
  src_x   = 5
  src_y   = 5
  dst_x   = 5
  dst_y   = 5
  opaque  = 5
  payload = 5

  def set( self, src_x, src_y, dst_x, dst_y, opaque, payload ):
    self.src_x   = src_x
    self.src_y   = src_y
    self.dst_x   = dst_x
    self.dst_y   = dst_y
    self.opaque  = opaque
    self.payload = payload
