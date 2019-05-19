#=========================================================================
# Flit.py
#=========================================================================
# Flit format for OCN generator
#
# Author : Cheng Tan
#   Date : Mar 30, 2019

from pymtl                 import *
from ocn_pclib.ifcs.Packet import *

import py

#-------------------------------------------------------------------------
# Dynamically generated MeshFlit
#-------------------------------------------------------------------------

_mesh_flit_dict = dict()
_mesh_flit_template = """
class MeshFlit{packet_size}_{mesh_wid}_by_{mesh_ht}( object ):
  def __init__( s ):
    s.IDType   = mk_bits   ( clog2( {packet_size} ) )
    s.XType    = mk_bits   ( clog2( {mesh_wid}    ) )
    s.YType    = mk_bits   ( clog2( {mesh_ht}     ) )
    s.TpType   = mk_bits   ( clog2( 4             ) )
    s.id       = s.IDType  ( 0 )
    s.src_x    = s.XType   ( 0 )
    s.src_y    = s.YType   ( 0 )
    s.dst_x    = s.XType   ( 0 )
    s.dst_y    = s.YType   ( 0 )
    s.type     = s.TpType  ( 0 )
    s.opaque   = Bits1     ( 0 )
    s.payload  = BasePacket(   ) 

  def fill( s, id, pkt ):
    s.id    = s.IDType ( id      )
    s.src_x = s.XType  ( pkt.src%{mesh_wid} )
    s.src_y = s.YType  ( pkt.src/{mesh_wid} )
    s.dst_x = s.XType  ( pkt.dst%{mesh_wid} )
    s.dst_y = s.YType  ( pkt.dst/{mesh_wid} )

    HEAD = 0
    BODY = 1
    TAIL = 2
    if id == 0:
      s.type = s.TpType( HEAD )
    elif id == {packet_size} - 1:
      s.type = s.TpType( TAIL )
    else:
      s.type = s.TpType( BODY )

    s.opaque  = Bits1  ( pkt.opaque  )
    s.payload = pkt 

  def __str__( s ):
    return "{{}}:({{}},{{}})>({{}},{{}}):{{}}:{{}}:{{}}".format(
      s.id, s.src_x, s.src_y, s.dst_x, s.dst_y, s.type, s.opaque, s.payload.payload )

_mesh_flit_dict[ ({packet_size}, {mesh_wid}, {mesh_ht}) ] = \
                MeshFlit{packet_size}_{mesh_wid}_by_{mesh_ht}
"""

def mk_mesh_flit( size, wid, ht ):
  if ( size, wid, ht ) in _mesh_flit_dict:
    return _mesh_flit_dict[ ( size, wid, ht ) ]
  else:
    print ( size, wid, ht )
    exec py.code.Source(
      _mesh_flit_template.format( packet_size = size, mesh_wid = wid, mesh_ht = ht )
    ).compile() in globals()
    return _mesh_flit_dict[ ( size, wid, ht ) ]

def flitisize_mesh_flit( pkt, size, wid, ht ):
  FlitType = mk_mesh_flit( size, wid, ht )
  flits = []
  for i in range( size ):
    flit = FlitType()
    flit.fill( i, pkt )
    flits.append( flit )
  return flits

#-------------------------------------------------------------------------
# Dynamically generated RingFlit
#-------------------------------------------------------------------------

_ring_flit_dict = dict()
_ring_flit_template = """
class RingFlit{packet_size}_{num_nodes}( object ):
  def __init__( s ):
    s.IDType   = mk_bits   ( clog2( {packet_size} ) )
    s.NType    = mk_bits   ( clog2( {num_nodes}   ) )
    s.TpType   = mk_bits   ( clog2( 4             ) )
    s.id       = s.IDType  ( 0 )
    s.src      = s.NType   ( 0 )
    s.dst      = s.NType   ( 0 )
    s.type     = s.TpType  ( 0 )
    s.opaque   = Bits1     ( 0 )
    s.payload  = BasePacket(   )

  def fill( s, id, pkt ):
    s.id   = s.IDType ( id      )
    s.src  = s.NType  ( pkt.src )
    s.dst  = s.NType  ( pkt.dst )

    HEAD = 0
    BODY = 1
    TAIL = 2
    if id == 0:
      s.type = s.TpType( HEAD )
    elif id == {packet_size} - 1:
      s.type = s.TpType( TAIL )
    else:
      s.type = s.TpType( BODY )

    s.opaque  = Bits1  ( pkt.opaque  )
    s.payload = pkt

  def __str__( s ):
    return "{{}}:({{}})>({{}}):{{}}:{{}}:{{}}".format(
      s.id, s.src, s.dst, s.type, s.opaque, s.payload.payload )

_ring_flit_dict[ ({packet_size}, {num_nodes}) ] = \
                RingFlit{packet_size}_{num_nodes}
"""

def mk_ring_flit( size, num_nodes ):
  if ( size, num_nodes ) in _ring_flit_dict:
    return _ring_flit_dict[ ( size, num_nodes ) ]
  else:
    exec py.code.Source(
      _ring_flit_template.format( packet_size = size, num_nodes = num_nodes )
    ).compile() in globals()
    return _ring_flit_dict[ ( size, num_nodes ) ]

def flitisize_ring_flit( pkt, size, num_nodes ):
  FlitType = mk_ring_flit( size, num_nodes )
  flits = []
  for i in range( size ):
    flit = FlitType()
    flit.fill( i, pkt )
    flits.append( flit )
  return flits

#    s.payload  = Bits16   ( 0 )
#    s.payload = Bits16 ( pkt.payload )
