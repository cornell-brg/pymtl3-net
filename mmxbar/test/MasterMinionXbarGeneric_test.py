'''
==========================================================================
MasterMinionXbarGeneric_test.py
==========================================================================
Tests for the generic master-minion xbar.

Author : Yanghui Ou
  Date : Apr 20, 2020
'''
import pytest
from pymtl3 import *
from pymtl3.stdlib.ifcs import mk_mem_msg, MemMsgType
from pymtl3.stdlib.cl.MemoryCL import MemoryCL
from pymtl3.stdlib.test.test_srcs import TestSrcCL as TestSource
from pymtl3.stdlib.test.test_sinks import TestSinkCL as TestSink
from pymtl3.stdlib.test import run_sim, mk_test_case_table

from ..MasterMinionXbarGeneric import MasterMinionXbarGeneric as Xbar

#-------------------------------------------------------------------------
# constants
#-------------------------------------------------------------------------

Req, Resp = mk_mem_msg( 8, 32, 32 )
rd = MemMsgType.READ
wr = MemMsgType.WRITE

hexwords = [
  0x8badf00d, 0xdeadbeef, 0xfeedbabe, 0xdeadc0de, 0xc001d00d,
  0xdeadfa11, 0xfaceb00c, 0xc001cafe, 0xdeafbabe, 0x8badcafe,
]

#-------------------------------------------------------------------------
# req
#-------------------------------------------------------------------------

def req( type_, opq, addr, data ):
  return Req( type_, opq, addr, 0, data )

#-------------------------------------------------------------------------
# resp
#-------------------------------------------------------------------------

def resp( type_, opq, test, data ):
  return Resp( type_, opq, test, 0, data )

#-------------------------------------------------------------------------
# mk_src_sink_msgs
#-------------------------------------------------------------------------

def mk_src_sink_msgs( msgs ):
  src_msgs =  [ lst[::2]  for lst in msgs ]
  sink_msgs = [ lst[1::2] for lst in msgs ]
  return src_msgs, sink_msgs

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, ncaches, max_req_in_flight, src_msgs, sink_msgs ):

    # Components

    s.src  = [ TestSource( Req, src_msgs[i] ) for i in range( ncaches ) ]
    s.sink = [ TestSink( Resp, sink_msgs[i] ) for i in range( ncaches ) ]
    s.dut  = Xbar( Req, Resp, ncaches, 1, max_req_in_flight )
    s.mem  = MemoryCL( 1, [ ( Req, Resp ) ], latency=5 )

    # Connections

    for i in range( ncaches ):
      connect( s.src[i].send,        s.dut.minion[i].req )
      connect( s.dut.minion[i].resp, s.sink[i].recv      )

    connect( s.dut.master[0], s.mem.ifc[0] )

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
# test case: req sanity check
#-------------------------------------------------------------------------

def test_sanity():
  dut = Xbar( Req, Resp, 2, 1 )
  dut.elaborate()
  dut.apply( SimulationPass() )
  dut.sim_reset()
  dut.tick()
  dut.tick()
  dut.tick()

  th = TestHarness( 2, 2, [ [], [] ], [ [], [] ] )
  th.elaborate()
  th.apply( SimulationPass() )
  th.sim_reset()
  th.tick()
  th.tick()
  th.tick()

#-------------------------------------------------------------------------
# test case: 1msg
#-------------------------------------------------------------------------

def one_msg( ncaches ):
  msgs    = [ [] for _ in range( ncaches ) ]
  msgs[1] = [
    req( wr, 0x1, 0x0000_1000, 0xfaceb00c_deadbeef_8badf00d_deafd00d ), resp( wr, 0x1, 0, 0 ),
  ]
  return mk_src_sink_msgs( msgs )

#-------------------------------------------------------------------------
# test case: wr rd each
#-------------------------------------------------------------------------
# each cache performs a write followed by a read to the same address.

def wr_rd_each_msg( ncaches ):
  msgs    = [ [] for _ in range( ncaches ) ]
  for i in range( ncaches ):
    msgs[i].append( req( wr, i, 0x1000*i, hexwords[i] ) )
    msgs[i].append( resp( wr, i, 0, 0 ) )
    msgs[i].append( req( rd, i, 0x1000*i, 0 ) )
    msgs[i].append( resp( rd, i, 0, hexwords[i] ) )
  return mk_src_sink_msgs( msgs )

#-------------------------------------------------------------------------
# test case: stream
#-------------------------------------------------------------------------

def stream_msg( ncaches ):
  msgs = [ [] for _ in range( ncaches ) ]
  for i in range( 20 ):
    msgs[0].append( req( wr, i, 0x1000*i, hexwords[i%10] ) )
    msgs[0].append( resp( wr, i, 0, 0 ) )

  for i in range( 20 ):
    msgs[0].append( req( rd, i, 0x1000*i,0 ) )
    msgs[0].append( resp( rd, i, 0, hexwords[i%10] ) )
  return mk_src_sink_msgs( msgs )

#-------------------------------------------------------------------------
# test case table
#-------------------------------------------------------------------------

test_cases = [
  (            'msg_func         ncaches max_in_flight lat init        intv' ),
  [ '1pkt_2',   one_msg,         2,      4,            5,  [0,9,   ],  [0,0    ] ],
  [ '1pkt_4',   one_msg,         4,      4,            3,  [0,9,0,0],  [9,0,9,0] ],
  [ 'wr_rd_2',  wr_rd_each_msg,  2,      4,            4,  [0,9,   ],  [0,0    ] ],
  [ 'wr_rd_4',  wr_rd_each_msg,  4,      4,            6,  [0,9,0,0],  [0,9,0,9] ],
  [ 'stream',   stream_msg,      2,      8,            5,  [0,100   ], [0,0    ] ],
  [ 'stream_d', stream_msg,      2,      4,            3,  [0,100   ], [0,0    ] ],
]

test_case_table = mk_test_case_table( test_cases )

#-------------------------------------------------------------------------
# test driver
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_reqresp_net( test_params ):
  ncaches             = test_params.ncaches
  max_in_flight       = test_params.max_in_flight
  init_delay          = test_params.init
  intv_delay          = test_params.intv
  src_msgs, sink_msgs = test_params.msg_func( test_params.ncaches )

  th = TestHarness( ncaches, max_in_flight, src_msgs, sink_msgs )
  th.set_param( 'top.mem.construct', latency=test_params.lat )
  for i in range( ncaches ):
    th.set_param( f'top.sink[{i}].construct',
      initial_delay=init_delay[i],
      interval_delay=intv_delay[i],
     )

  run_sim( th )
