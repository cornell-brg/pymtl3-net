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
from pymtl3.stdlib.mem import mk_mem_msg, MemMsgType, MagicMemoryCL as MemoryCL
from pymtl3.stdlib.stream.SourceRTL import SourceRTL as TestSource
from pymtl3.stdlib.stream.SinkRTL import SinkRTL as TestSink
from pymtl3.stdlib.stream.ifcs import MinionIfcRTL
from pymtl3.stdlib.stream.valrdy_master_minion_ifcs import MasterIfcCL
# from pymtl3.stdlib.stream.valrdy_master_minion_ifcs import ValRdyMasterMinionRTL2CLAdapter
from pymtl3.stdlib.test_utils import run_sim, mk_test_case_table

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
  # PP: I have to allow truncation because the int is too big to fit into
  # a Bits32.
  TypeData = mk_bits( Req.get_field_type('data').nbits )
  return Req( type_, opq, addr, 0, TypeData( data, trunc_int=True ) )

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
# Adapter
#-------------------------------------------------------------------------

from pymtl3.extra import clone_deepcopy

class ValRdyMasterMinionRTL2CLAdapter( Component ):

  def req_rdy( s ):
    return s.req_entry is not None

  def req( s ):
    assert s.req_entry is not None
    ret = s.req_entry
    s.req_entry = None
    return ret

  def resp_rdy( s ):
    return s.resp_entry is None

  def resp( s, msg ):
    s.resp_entry = clone_deepcopy( msg )

  def construct( s, ReqType, RespType ):
    s.left  = MinionIfcRTL( ReqType, RespType )
    s.right = MasterIfcCL( ReqType, RespType, resp=s.resp, resp_rdy=s.resp_rdy )

    # Req side

    s.req_entry = None

    @update_ff
    def up_left_req_rdy():
      s.left.req.rdy <<= (s.req_entry is None)

    @update_once
    def up_left_req_msg():
      if s.req_entry is None:
        if s.left.req.val:
          s.req_entry = clone_deepcopy( s.left.req.msg )

    @update_once
    def up_right_req():
      if ( not s.req_entry is None ) and s.right.req.rdy():
        s.right.req( clone_deepcopy( s.req_entry ) )
        s.req_entry = None


    s.add_constraints(
      U( up_left_req_msg ) < M( s.req ),
      U( up_left_req_msg ) < M( s.req_rdy    ),
      U(up_left_req_msg  ) < U( up_right_req ),
    )

    # Resp side

    s.resp_entry = None
    s.resp_sent  = Wire()

    @update_once
    def up_right_resp():
      if s.resp_entry is None:
        s.left.resp.val @= 0
      else:
        s.left.resp.val @= 1
        s.left.resp.msg @= s.resp_entry

    @update_ff
    def up_resp_sent():
      s.resp_sent <<= s.left.resp.val & s.left.resp.rdy

    @update_once
    def up_clear():
      if s.resp_sent: # constraints reverse this
        s.resp_entry = None

    s.add_constraints(
      U( up_clear )   < M( s.resp ),
      U( up_clear )   < M( s.resp_rdy ),
      M( s.resp )     < U( up_right_resp ),
      M( s.resp_rdy ) < U( up_right_resp )
    )

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, ncaches, max_req_in_flight, src_msgs, sink_msgs ):

    # Components

    s.src  = [ TestSource( Req, src_msgs[i] ) for i in range( ncaches ) ]
    s.sink = [ TestSink( Resp, sink_msgs[i] ) for i in range( ncaches ) ]
    s.dut  = Xbar( Req, Resp, ncaches, 1, max_req_in_flight )

    s.adapter = ValRdyMasterMinionRTL2CLAdapter( Req, Resp )
    s.mem  = MemoryCL( 1, [ ( Req, Resp ) ], latency=5 )

    # Connections

    for i in range( ncaches ):
      connect( s.src[i].send,        s.dut.minion[i].req )
      connect( s.dut.minion[i].resp, s.sink[i].recv      )

    connect( s.dut.master[0], s.adapter.left )
    connect( s.adapter.right, s.mem.ifc[0] )

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
  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()
  dut.sim_tick()

  th = TestHarness( 2, 2, [ [], [] ], [ [], [] ] )
  th.elaborate()
  th.apply( DefaultPassGroup() )
  th.sim_reset()
  th.sim_tick()
  th.sim_tick()
  th.sim_tick()

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
