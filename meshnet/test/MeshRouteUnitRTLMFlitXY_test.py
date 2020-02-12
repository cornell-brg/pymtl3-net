'''
==========================================================================
MeshRouteUnitRTLMFlitXY_test.py
==========================================================================
Unit tests for the multi-flit mesh route unit.

Author : Yanghui Ou
  Date : 11 Feb, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.rtl.queues import BypassQueueRTL
# from pymtl3.stdlib.test import run_sim
from ocnlib.utils import to_bits, to_bitstruct
from ocnlib.test.test_srcs import MultiFlitPacketSourceRTL as TestSource
from ocnlib.test.test_sinks import MultiFlitPacketSinkRTL as TestSink
from ocnlib.packets import MultiFlitPacket as Packet

from ..directions import *
from ..MeshRouteUnitRTLMFlitXY import MeshRouteUnitRTLMFlitXY

#-------------------------------------------------------------------------
# Helper stuff
#-------------------------------------------------------------------------

# TODO: use stdlib run_sim omce pymtl3 is updated
def run_sim( th, max_cycles=200 ):
  th.elaborate()
  th.apply( SimulationPass() )
  th.sim_reset()

  ncycles = 0
  while not th.done() and ncycles < max_cycles:
    print( f'{ncycles:3}:{th.line_trace()}' )
    th.tick()

  assert th.done()
  th.tick()
  th.tick()
  th.tick()

def route_unit_fl( HeaderFormat, pkt_lst, pos_x, pos_y, first_dimension='x' ):
  sink_pkts = [ [] for _ in range(5) ]
  if first_dimension == 'x':
    for pkt in pkt_lst:
      header = to_bitstruct( pkt.flits[0], HeaderFormat )
      if header.dst_x == pos_x and header.dst_y == pos_y:
        sink_pkts[ SELF ].append( pkt )
      elif header.dst_x < pos_x:
        sink_pkts[ WEST ].append( pkt )
      elif header.dst_x > pos_x:
        sink_pkts[ EAST ].append( pkt )
      elif header.dst_y < pos_y:
        sink_pkts[ SOUTH ].append( pkt )
      else:
        sink_pkts[ NORTH ].append( pkt )

  elif first_dimension == 'y':
    for pkt in pkt_lst:
      header = to_bitstruct( pkt.flits[0], HeaderFormat )
      if header.dst_x == pos_x and header.dst_y == pos_y:
        sink_pkts[ SELF ].append( pkt )
      elif s.header.dst_y < pos_y:
        sink_pkts[ NORTH ].append( pkt )
      elif s.header.dst_y > pos_y:
        sink_pkts[ SOUTH ].append( pkt )
      elif s.header.dst_x < pos_x:
        sink_pkts[ WEST ].append( pkt )
      else:
        sink_pkts[ EAST ].append( pkt )

  else:
    assert False

  return sink_pkts

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):
  def construct( s, HeaderFormat, PositionType, pkts, x, y ):
    PhitType = mk_bits( get_nbits( HeaderFormat ) )
    sink_pkts = route_unit_fl( HeaderFormat, pkts, x, y )
    print( sink_pkts )

    s.src   = TestSource( HeaderFormat, pkts )
    s.src_q = BypassQueueRTL( PhitType, num_entries=1 )
    s.dut   = MeshRouteUnitRTLMFlitXY( HeaderFormat, PositionType )
    s.sink  = [ TestSink( HeaderFormat, sink_pkts[i] ) for i in range(5) ]

    s.src.send  //= s.src_q.enq
    s.src_q.deq //= s.dut.get
    s.dut.pos   //= PositionType( x, y )
    
    for i in range(5):
      s.sink[i].recv.msg //= s.dut.give[i].msg 
      s.sink[i].recv.en  //= lambda: s.dut.give[i].rdy & s.sink[i].recv.rdy
      s.dut.give[i].en   //= lambda: s.dut.give[i].rdy & s.sink[i].recv.rdy

  def done( s ):
    sinks_done = True
    for sink in s.sink:
      sinks_done &= sink.done()
    return s.src.done() and sinks_done
  
  def line_trace( s ):
    return s.dut.line_trace()

#-------------------------------------------------------------------------
# TestHeader
#-------------------------------------------------------------------------

@bitstruct
class TestHeader:
  opaque: Bits8
  plen  : Bits8
  src_x : Bits4
  src_y : Bits4
  dst_x : Bits4
  dst_y : Bits4

#-------------------------------------------------------------------------
# TestPosition
#-------------------------------------------------------------------------

@bitstruct
class TestPosition:
  pos_x : Bits4
  pos_y : Bits4

#-------------------------------------------------------------------------
# mk_pkt
#-------------------------------------------------------------------------

def mk_pkt( dst_x, dst_y, payload=[], src_x=0, src_y=0, opaque=0 ):
  plen        = len( payload )
  header      = TestHeader( opaque, plen, src_x, src_y, dst_x, dst_y )
  header_bits = to_bits( header )
  flits       = [ header_bits ] + payload
  return Packet( TestHeader, flits )

#-------------------------------------------------------------------------
# test_1pkt
#-------------------------------------------------------------------------

def test_1pkt():
  pkts= [
    mk_pkt( 0, 1, [ 0xfaceb00c, 0x8badf00d ] ), 
  ]
  th = TestHarness( TestHeader, TestPosition, pkts, 0, 0 )
  run_sim( th, max_cycles=20 )
