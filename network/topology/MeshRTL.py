#=========================================================================
# MeshRTL.py
#=========================================================================
# Initial implementation of Mesh topology
#
# Author : Cheng Tan
#   Date : Mar 10, 2019

from pymtl import *
from pclib.ifcs.EnRdyIfc  import InEnRdyIfc, OutEnRdyIfc

class MeshRTL( RTLComponent ):
  def construct( s, routers ):
