#=========================================================================
# PitonXbar_test.py
#=========================================================================
# Test for PitonXbar
#
# Author : Cheng Tan
#   Date : Dec 17, 2019

import pytest
import random
import hypothesis
from   hypothesis import strategies as st

from pymtl3 import *
from pymtl3.stdlib.test.test_srcs import TestSrcRTL
from pymtl3.stdlib.test import mk_test_case_table
from ocn_pclib.test.net_sinks import TestNetSinkRTL

from ..Deserializer import Deserializer
from ..Serializer   import Serializer
from ..PitonNetMsg  import *
from ..PitonXbar    import PitonXbar

from ocn_pclib.ifcs.enrdy_adapters import *

#------------------------------------------------------------------------------
# Test Harness
#------------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, num_ports,
                 src_msgs, sink_msgs, src_delay, sink_delay,
                 dump_vcd=False, test_verilog=False ):

    msg_type     = mk_piton_net_msg()
    s.num_ports  = num_ports
    s.src_msgs   = src_msgs
    s.sink_msgs  = sink_msgs
    s.src_delay  = src_delay
    s.sink_delay = sink_delay
    match_func = lambda a, b : 1==1
#    match_func = lambda a, b : a.payload == b.payload and a.xpos == b.xpos and\
#                               a.ypos == b.ypos

    s.xbar = PitonXbar( num_ports=num_ports )
    s.src_adapter = [ EnRdy2ValRdy( msg_type ) for i in range( num_ports ) ]
    s.src  = [ TestSrcRTL ( msg_type, s.src_msgs[i], s.src_delay )
               for i in range( num_ports ) ]
    s.sink_adapter = [ ValRdy2EnRdy( msg_type ) for i in range( num_ports ) ]
    s.sink = [ TestNetSinkRTL( msg_type, s.sink_msgs[i], s.sink_delay,
                               match_func = match_func )
               for i in range( num_ports ) ]

    s.ser = [   Serializer() for _ in range( num_ports ) ]
    s.des = [ Deserializer() for _ in range( num_ports ) ]

    # Dump vcd

    if dump_vcd:
      s.xbar.vcd_file = dump_vcd
      if hasattr( s.xbar, 'inner' ):
        s.xbar.inner.vcd_file = dump_vcd

    # Test verilog

    if test_verilog:
      s.xbar = TranslationTool( s.xbar )

    # Connections
    for i in range( num_ports ):
      s.src[i].send         //=  s.src_adapter[i].in_
      s.src_adapter[i].out  //=  s.ser[i].in_
      s.ser[i].out          //=  s.xbar.in_[i]
      s.xbar.out[i]         //=  s.des[i].in_
      s.des[i].out          //=  s.sink_adapter[i].in_
      s.sink_adapter[i].out //=  s.sink[i].recv

  def done( s ):
    done_flag = 1
    for i in range( s.num_ports ):
      done_flag &= s.src[i].done() and s.sink[i].done()
    return done_flag

  def line_trace( s ):
    return "\n in0 : {}\n in1 : {}\n {} out0: {}\n out1: {}\n".format(
            s.ser[0].line_trace(), s.ser[1].line_trace(),
            s.xbar.line_trace(),
            s.des[0].line_trace(), s.des[1].line_trace()
            )

#------------------------------------------------------------------------------
#  run_xbar_test
#------------------------------------------------------------------------------

def run_xbar_test( nports, src_delay, sink_delay, test_msgs,
                   dump_vcd=False, test_verilog=False ):

  max_cycles = 1000

  # src/sin msgs
  src_msgs  = test_msgs[0]
  sink_msgs = test_msgs[1]

  th = TestHarness( nports, src_msgs, sink_msgs, src_delay, sink_delay,
                    dump_vcd, test_verilog )
  th.vcd_file     = dump_vcd
  th.test_verilog = test_verilog
  th.elaborate()

  th.apply( SimulationPass() )
  # sim = SimulationTool( model )

  th.reset()
  ncycles = 0
  print()
  print( "{:3}:{}".format( ncycles, th.line_trace() ))
  while not th.done() and ncycles < max_cycles:
    th.tick()
    ncycles += 1
    print( "{:3}:{}".format( ncycles, th.line_trace() ))

  # Check timeout
  assert ncycles < max_cycles

#------------------------------------------------------------------------------
# Helper stuff
#------------------------------------------------------------------------------

def mk_test_msgs( nports, msg_list ):

  src_msgs   = [ [] for _ in range( nports ) ]
  sink_msgs  = [ [] for _ in range( nports ) ]

  for m in msg_list:
    src, dest, chipid, plen, msg_type, payload = \
      m[0], m[1], m[2], m[3], m[4], m[5]
    chipid_bits = Bits( 14, chipid)
    xpos = nports - 1 if chipid_bits[13] == 1 else dest
    #                                    xpos  ypos fbits plen  msg_type  tag options
    msg = mk_piton_msg( payload, chipid, xpos, 0,   0,    plen, msg_type, 0,  0)

    src_msgs [ src].append( msg )
    sink_msgs[dest].append( msg )

  return [ src_msgs, sink_msgs ]

#-------------------------------------------------------------------------------
# Directed tests - msg_type and nports are not yet used
#-------------------------------------------------------------------------------

# chip id indicating that the message was to be sent offchip
offchip = Bits( 14, 0 )
offchip[13] = 1

payload0 = 0
payload1 = 0xdeaddeaddeaddead
payload2 = 0x2222222222222222deaddeaddeaddead
payload6 = 0x66666666666666665555555555555555444444444444444433333333333333332222222222222222deaddeaddeaddead

payload = [
 0,
 0xdeaddeaddeaddead,
 0x2222222222222222deaddeaddeaddead,
 0x33333333333333332222222222222222deaddeaddeaddead,
 0x444444444444444433333333333333332222222222222222deaddeaddeaddead,
 0x5555555555555555444444444444444433333333333333332222222222222222deaddeaddeaddead,
 0x66666666666666665555555555555555444444444444444433333333333333332222222222222222deaddeaddeaddead
]
def basic_msg( nports ):
  return mk_test_msgs( nports,
    #   src  dest  chip_id plen, msg_type, payload
    [ ( 0,   0,    0,      2,    31,        payload[2] ),
      #( 0,   0,    0,      2,    31,        payload[2] )
    ] )

def basic_2msgs( nports ):
  return mk_test_msgs( nports,
    #   src  dest  chip_id plen, msg_type, payload
    [ ( 0,   0,    0,      1,    0,        payload[1] ),
      ( 0,   0,    0,      6,    14,       payload[6] ),
      ( 1,   0,    0,      6,    19,       payload[6] )
    ] )

def basic_offchip( nports ):
  return mk_test_msgs( nports,
    #   src  dest  chip_id  plen, msg_type, payload
    [ ( 0,   0,    0,       1,    0,        payload[1] ),
      ( 1,   0,    0,       1,    0,        payload[1] ),
      ( 0,   1,    offchip, 1,    0,        payload[1] )
    ] )

def offchip_to_noc( nports ):
  return mk_test_msgs( nports,
    #   src  dest  chip_id  plen, msg_type, payload
    [ ( 1,   0,    0,       1,    0,        payload[1] ),
      ( 1,   0,    0,       6,    0,        payload[6] ),
      ( 0,   1,    offchip, 1,    0,        payload[1] )
    ] )

def noc_to_offchip( nports ):
  return mk_test_msgs( nports,
    #   src  dest  chip_id  plen, msg_type, payload
    [ ( 1,   0,    0,       0,    33,       payload[0] ),
      ( 0,   0,    0,       1,    14,       payload[1] ),
      ( 0,   1,    offchip, 2,    19,       payload[2] )
    ] )

def zero_plen( nports ):
  return mk_test_msgs( nports,
    #   src  dest  chip_id  plen, msg_type, payload
    [ #( 1,   0,    0,       0,    33,       payload[0]        ),
      ( 0,   0,    0,       0,    14,       payload[0]        ),
      ( 0,   0,    0,       0,    14,       payload[0]        ),
      ( 0,   1,    offchip, 0,    19,       payload[0]        )
    ] )

def direct0( nports ):
  return mk_test_msgs( nports,
    #   src  dest  chip_id  plen, msg_type, payload
    [ ( 0,   0,    0,       1,    33,       payload[1]        ),
      ( 0,   0,    0,       0,    14,       payload[0]        ),
    ] )

def direct1( nports ):
  return mk_test_msgs( nports,
    #   src  dest  chip_id  plen, msg_type, payload
    [ ( 1,   0,    0,       1,    33,       payload[1]        ),
      ( 0,   0,    0,       0,    14,       payload[0]        ),
    ] )

def three_ports( nports ):
  return mk_test_msgs( nports,
    #   src  dest  chip_id  plen, msg_type, payload
    [ ( 1,   0,    0,       1,    33,       payload[1]        ),
      ( 1,   2,    offchip, 1,    33,       payload[1]        ),
      ( 0,   1,    0,       1,    14,       payload[1]        ),
      ( 0,   2,    offchip, 2,    14,       payload[2]        ),

    ] )

#-------------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------------
# nports is not yet used
#
test_case_table = mk_test_case_table([
  (          "      msg_func        nports src_delay sink_delay" ),
  ["basic1",        basic_msg,      2,     0,        0           ],
#  ["basic2",        basic_2msgs,    2,     0,        0           ],
#  ["offchip",       basic_offchip,  2,     0,        0           ],
#  ["offchip_delay", basic_offchip,  2,     5,        5           ],
#  ["offchip2noc",   offchip_to_noc, 2,     0,        0           ],
#  ["noc2offchip",   noc_to_offchip, 2,     0,        0           ],
#  ["0plen",         zero_plen,      2,     0,        0           ],
#  ["direct0",       direct0,        2,     0,        0           ],
#  ["direct1",       direct1,        2,     0,        0           ],
#  ["3ports",        three_ports,    3,     0,        0           ]
])

#-------------------------------------------------------------------------------
# Run Tests
#-------------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_direct( test_params, dump_vcd, test_verilog ):
  test_msgs = test_params.msg_func( test_params.nports )
  run_xbar_test( test_params.nports,
		 test_params.src_delay, test_params.sink_delay, test_msgs,
                 dump_vcd, test_verilog )

## Hypothesis test
#@hypothesis.strategies.composite
#def xbar_test_msg( draw, nports ):
#  src      = draw( st.integers( 0, nports - 1  ) )
#  dest     = draw( st.integers( 0, nports - 1  ) )
#  plen     = draw( st.integers( 0, 6  ) )
#  msg_type = draw( st.integers( 0, 31 ) )
#  # Offchip port won't send a packet to itself
#  hypothesis.assume( not( src == nports-1 and dest == nports - 1 ) )
#  chip_id = offchip if dest==nports-1 else 0
#  return ( src, dest, chip_id, plen, msg_type, payload[plen] )
#
#@hypothesis.given(
#  src_delay  = st.integers( 0, 10 ),
#  sink_delay = st.integers( 0, 10 ),
#  test_msgs  = st.data()
#)
#@hypothesis.settings( max_examples = 500, deadline = 1000 )
#def test_hypothesis_2ports( src_delay, sink_delay, test_msgs,
#		                        dump_vcd, test_verilog ):
#  msgs = test_msgs.draw( st.lists( xbar_test_msg( 2 ),
#                         min_size = 1, max_size = 15 ) )
#  run_xbar_test( 2, src_delay, sink_delay, mk_test_msgs( 2, msgs ),
#                dump_vcd, test_verilog )
#
#@hypothesis.given(
#  nports     = st.integers( 2, 8  ),
#  src_delay  = st.integers( 0, 10 ),
#  sink_delay = st.integers( 0, 10 ),
#  test_msgs  = st.data()
#)
#@hypothesis.settings( max_examples = 500, deadline = 10000 )
#def test_hypothesis_nports( nports, src_delay, sink_delay, test_msgs,
#		                        dump_vcd, test_verilog ):
#  msgs = test_msgs.draw( st.lists( xbar_test_msg( nports ),
#                         min_size = 1, max_size = 15 ) )
#  run_xbar_test( nports, src_delay, sink_delay, mk_test_msgs( nports, msgs ),
#                dump_vcd, test_verilog )
