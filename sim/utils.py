"""
==========================================================================
utils.py
==========================================================================
Utility functions for pyocn script.

Author: Yanghui Ou
  Date: Sep 24, 2019
"""

import sys
import os
import argparse
import subprocess

# Hacky way to add pymtl3-net to path
# TODO: remove this line and use globally installed pymtl3-net
sys.path.insert(0, os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )

from meshnet import MeshNetworkRTL
from ringnet import RingNetworkRTL

#-------------------------------------------------------------------------
# module level variable
#-------------------------------------------------------------------------

verbose = False

#-------------------------------------------------------------------------
# Verbose print
#-------------------------------------------------------------------------

def vprint( msg, value=None ):
  if verbose:
    if value is not None:
      print( msg, value )
    else:
      print( msg )

#-------------------------------------------------------------------------
# add_mesh_arg
#-------------------------------------------------------------------------

def _add_mesh_arg( p ):
  p.add_argument( '--ncols', type=int, default=2, metavar='' )
  p.add_argument( '--nrows', type=int, default=2, metavar='' )
  p.add_argument( '--channel-lat', type=int, default=0, metavar='' )

#-------------------------------------------------------------------------
# add_ring_arg
#-------------------------------------------------------------------------

def _add_ring_arg( p ):
  p.add_argument( '--nterminals',  type=int, default=4, metavar='' )
  p.add_argument( '--channel-lat', type=int, default=0, metavar='' )

#-------------------------------------------------------------------------
# _mk_mesh
#-------------------------------------------------------------------------

def _mk_mesh( opts ):
  ...

#-------------------------------------------------------------------------
# _mk_ring
#-------------------------------------------------------------------------

def _mk_ring( opts ):
  ...

#-------------------------------------------------------------------------
# dictionaries
#-------------------------------------------------------------------------

_net_arg_dict = {
  'mesh' : _add_mesh_arg,
  'ring' : _add_ring_arg,
}

_net_type_dict = {
  'mesh' : MeshNetworkRTL,
  'ring' : RingNetworkRTL,
}

#-------------------------------------------------------------------------
# mk_net_arg_parser
#-------------------------------------------------------------------------

def mk_net_arg_parser( topo ):
  if not topo in _net_arg_dict:
    raise Exception( f'Unkonwn network topology {topo}' )

  p = argparse.ArgumentParser(
    # description = f'{topo}',
    usage = f'./pyocn sim {topo} [<flags>]',
  )
  p.add_argument( '-v', '--verbose', action='store_true', help='Run in verbose mode.' )
  p.add_argument( '-s', '--trace',   action='store_true', help='Show line trace.'    )
  p.add_argument(       '--injection-rate', type=int, default=10, help='Injection rate in percentage. Default is 10.', metavar='' )
  p.add_argument(       '--pattern', type=int, default='urandom', help='Traffic pattern. Default is urandom.',  metavar='' )
  _net_arg_dict[ topo ]( p )
  return p

#-------------------------------------------------------------------------
# mk_net_inst
#-------------------------------------------------------------------------

def mk_net_inst( topo, opts ):
  ...