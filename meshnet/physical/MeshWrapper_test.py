'''
==========================================================================
MeshWrapper_test.py
==========================================================================
A simple translation test of MeshWrapper.

Author: Yanghui Ou
  Date: July 21, 2020
'''
import pytest
from random import randint
from pymtl3 import *
from pymtl3.passes.backends.verilog import *

from ocnlib.packets import MflitPacket as Packet
from ocnlib.test.test_srcs import MflitPacketSourceRTL as TestSource
from ocnlib.test.test_sinks import MflitPacketSinkRTL as TestSink
from ocnlib.utils import run_sim

from .MeshWrapper import MeshWrapper

@bitstruct
class Header64:
  src_x : Bits8
  src_y : Bits8
  dst_x : Bits8
  dst_y : Bits8
  plen  : Bits4
  filler: Bits28

@bitstruct
class Position:
  pos_x : Bits8
  pos_y : Bits8

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, Header, Position, ncols, nrows, src_pkts, sink_pkts ):
    nterminals = ncols * nrows

    s.src  = [ TestSource( Header, src_pkts[i] ) for i in range( nterminals ) ]
    s.dut  = MeshWrapper( Header, Position, ncols, nrows )
    s.sink = [ TestSink( Header, sink_pkts[i] ) for i in range( nterminals ) ]

    for i in range( nterminals ):
      s.src[i].send //= s.dut.recv[i]
      s.dut.send[i] //= s.sink[i].recv

    # Metadata

    s.dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'TiledMesh{ncols}x{nrows}' )
    s.dut.set_metadata( VerilogTranslationImportPass.enable, True )

  def done( s ):
    src_done = True
    sink_done = True
    for m in s.src:
      src_done &= m.done()
    for m in s.sink:
      sink_done &= m.done()
    return src_done and sink_done

  def line_trace( s ):
    return s.dut.line_trace()

#-------------------------------------------------------------------------
# mk_pkt
#-------------------------------------------------------------------------
# Generate a random packet from src to dst with random payload.

def mk_pkt( src_x, src_y, dst_x, dst_y, HeaderT, msg_nbits=512, opaque=0 ):
  phit_nbits = HeaderT.nbits
  assert msg_nbits % phit_nbits == 0
  PhitT       = mk_bits( phit_nbits )
  plen        = msg_nbits // phit_nbits
  header      = HeaderT( src_x, src_y, dst_x, dst_y, plen )
  header_bits = header.to_bits()
  payload     = [ PhitT( randint(0, 2**phit_nbits-1) ) for _ in range( plen ) ]
  flits       = [ header_bits ] + payload
  return Packet( HeaderT, flits )

#-------------------------------------------------------------------------
# gen_urandom_traffic
#-------------------------------------------------------------------------
# Generate uniform random traffic.

def gen_urandom_traffic( ncols, nrows, HeaderT, msg_nbits=512, packets_per_pair=10 ):
  phit_nbits = HeaderT.nbits
  assert msg_nbits % phit_nbits == 0

  pkts = []
  for src_x in range( ncols ):
    for src_y in range( nrows ):
      for dst_x in range( ncols ):
        for dst_y in range( nrows ):
          for _ in range( packets_per_pair ):
            pkts.append( mk_pkt( src_x, src_y, dst_x, dst_y, HeaderT, msg_nbits ) )

  return pkts

#-------------------------------------------------------------------------
# arrange_src_sink_pkts
#-------------------------------------------------------------------------

def arrange_src_sink_pkts( Header, ncols, nrows, pkt_lst ):
  nterminals = ncols * nrows
  src_pkts  = [ [] for _ in range( nterminals ) ]
  sink_pkts = [ [] for _ in range( nterminals ) ]

  for pkt in pkt_lst:
    header = Header.from_bits( pkt.flits[0] )
    src_id = header.src_x.uint() + header.src_y.uint() * ncols
    dst_id = header.dst_x.uint() + header.dst_y.uint() * ncols
    src_pkts [ src_id ].append( pkt )
    sink_pkts[ dst_id ].append( pkt )

  return src_pkts, sink_pkts

#-------------------------------------------------------------------------
# translation tests
#-------------------------------------------------------------------------

def test_translate2x2():
  assert Header64.nbits == 64
  assert Position.nbits == 16

  sys = MeshWrapper( Header64, Position, ncols=2, nrows=2 )
  sys.set_metadata( VerilogTranslationPass.explicit_module_name, f'TiledMesh2x2' )
  sys.set_metadata( VerilogTranslationImportPass.enable, True )

  sys.elaborate()
  sys = VerilogTranslationImportPass()( sys )

  sys.apply( DefaultPassGroup() )
  sys.sim_reset()
  sys.sim_tick()
  sys.sim_tick()

def test_translate4x4():
  assert Header64.nbits == 64
  assert Position.nbits == 16

  sys = MeshWrapper( Header64, Position, ncols=4, nrows=4 )
  sys.set_metadata( VerilogTranslationPass.explicit_module_name, f'TiledMesh4x4' )
  sys.set_metadata( VerilogTranslationImportPass.enable, True )

  sys.elaborate()
  sys = VerilogTranslationImportPass()( sys )

  sys.apply( DefaultPassGroup() )
  sys.sim_reset()
  sys.sim_tick()
  sys.sim_tick()

def test_translate6x6():
  assert Header64.nbits == 64
  assert Position.nbits == 16

  sys = MeshWrapper( Header64, Position, ncols=4, nrows=4 )
  sys.set_metadata( VerilogTranslationPass.explicit_module_name, f'TiledMesh6x6' )
  sys.set_metadata( VerilogTranslationImportPass.enable, True )

  sys.elaborate()
  sys = VerilogTranslationImportPass()( sys )

  sys.apply( DefaultPassGroup() )
  sys.sim_reset()
  sys.sim_tick()
  sys.sim_tick()

def test_translate8x8():
  assert Header64.nbits == 64
  assert Position.nbits == 16

  sys = MeshWrapper( Header64, Position, ncols=8, nrows=8 )
  sys.set_metadata( VerilogTranslationPass.explicit_module_name, f'TiledMesh8x8' )
  sys.set_metadata( VerilogTranslationImportPass.enable, True )

  sys.elaborate()
  sys = VerilogTranslationImportPass()( sys )

  sys.apply( DefaultPassGroup() )
  sys.sim_reset()
  sys.sim_tick()
  sys.sim_tick()

#-------------------------------------------------------------------------
# Energy test
#-------------------------------------------------------------------------

@pytest.mark.parametrize( 
  'ncols, nrows, pkts_per_pair', [
  ( 2, 2, 10 ),
])
def test_energy( ncols, nrows, pkts_per_pair, cmdline_opts ):
  traffic = gen_urandom_traffic( ncols, nrows, Header64, 512, pkts_per_pair )
  src_pkts, sink_pkts = arrange_src_sink_pkts( Header64, ncols, nrows, traffic )
  th = TestHarness( Header64, Position, ncols, nrows, src_pkts, sink_pkts )
  run_sim( th, cmdline_opts, max_cycles=10000 )

