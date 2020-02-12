'''
==========================================================================
src_sink_test.py
==========================================================================
Unit tests for sources and sinks.

Author : Yanghui Ou
  Date : Feb 3, 2019
'''
from pymtl3 import *
from ..packets   import packet_format, MultiFlitPacket
from .test_srcs  import MultiFlitPacketSourceCL
from .test_sinks import MultiFlitPacketSinkCL

@bitstruct
class SimpleFormat:
  opq  : Bits8
  src  : Bits8
  dst  : Bits8
  plen : Bits8

def mk_simple_pkt( src, dst, payload ):
  plen          = len(payload)
  header        = b32(0)
  header[0 :8 ] = b8(plen)
  header[8 :16] = b8(src)
  header[16:24] = b8(dst)
  flits = [ header ]
  flits.extend( [ b32(x) for x in payload ] )
  return MultiFlitPacket( SimpleFormat, flits )

class TestHarness( Component ):

  def construct( s, Format, pkts ):
    s.src  = MultiFlitPacketSourceCL( SimpleFormat, pkts )
    s.sink = MultiFlitPacketSinkCL  ( SimpleFormat, pkts )
    connect( s.src.send, s.sink.recv )

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return f'{s.src.line_trace()} >>> {s.sink.line_trace()}'

#-------------------------------------------------------------------------
# test_simple
#-------------------------------------------------------------------------

def test_simple():

  pkts = [
    mk_simple_pkt( 0, 1, [ 0xbeef, 0xb00c ] ),
    mk_simple_pkt( 1, 0, [ 0xf00d, 0xbabe ] ),
  ]
  th = TestHarness( SimpleFormat, pkts )
  th.elaborate()
  th.apply( SimulationPass() )

  print()
  for i in range(10):
    th.tick()
    print( f'{i:3}:{th.line_trace()}' )

  assert th.done()

#-------------------------------------------------------------------------
# test_src_delay
#-------------------------------------------------------------------------

def test_src_delay():
  pkts = [
    mk_simple_pkt( 0, 1, [ 0xbeef, 0xface, 0xf00d ] ),
    mk_simple_pkt( 0, 1, [ 0xbaad, 0xc0de         ] ),
  ]

  th = TestHarness( SimpleFormat, pkts )
  th.set_param( 'top.src.construct', initial_delay=5, flit_interval_delay=2 )
  th.elaborate()
  th.apply( SimulationPass() )
  print()
  for i in range( 25 ):
    th.tick()
    print( f'{i:3}:{th.line_trace()}' )
  assert th.done()

#-------------------------------------------------------------------------
# test_sink_delay
#-------------------------------------------------------------------------

def test_sink_delay():
  pkts = [
    mk_simple_pkt( 0, 1, [ 0xbeef, 0xface, 0xf00d ] ),
    mk_simple_pkt( 0, 1, [ 0xbaad, 0xc0de         ] ),
  ]

  th = TestHarness( SimpleFormat, pkts )
  th.set_param( 'top.sink.construct', initial_delay=5, flit_interval_delay=2 )
  th.elaborate()
  th.apply( SimulationPass() )
  print()
  for i in range( 25 ):
    th.tick()
    print( f'{i:3}:{th.line_trace()}' )
  assert th.done()

#-------------------------------------------------------------------------
# test_mix_delay
#-------------------------------------------------------------------------

def test_mix_delay():
  pkts = [
    mk_simple_pkt( 0, 1, [ 0xbeef, 0xface, 0xf00d ] ),
    mk_simple_pkt( 0, 1, [ 0xbaad, 0xc0de         ] ),
    mk_simple_pkt( 1, 1, [                        ] ),
    mk_simple_pkt( 2, 1, [ 0xcba                  ] ),
  ]

  th = TestHarness( SimpleFormat, pkts )
  th.set_param( 'top.sink.construct', initial_delay=5, flit_interval_delay=2 )
  th.set_param( 'top.src.construct',  packet_interval_delay=5 )
  th.elaborate()
  th.apply( SimulationPass() )
  print()
  for i in range( 50 ):
    th.tick()
    print( f'{i:3}:{th.line_trace()}' )
  assert th.done()