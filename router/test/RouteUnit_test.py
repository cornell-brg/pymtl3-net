import pytest
import hypothesis
from hypothesis import strategies as st

from pymtl import *
from pclib.test import TestVectorSimulator, TestSource, TestSink, mk_test_case_table
from router.RouteUnitDOR import RouteUnitDOR
from ifcs.SinglePhitPacket import SinglePhitPacket

import copy

#=======================================================================
# Test Harness
#=======================================================================
class TestHarness( Model ):
  """
  A test harness for DOR route unit.
  """
  def __init__( s, pkt_type, pos_x, pos_y, dimension,
                src_msgs, sink_msgs, src_delay, sink_delay, 
                dump_vcd=False, test_verilog=False ):
    # Constants
    s.src_msgs   = src_msgs
    s.sink_msgs  = sink_msgs
    s.src_delay  = src_delay
    s.sink_delay = sink_delay
    s.num_ports  = 5

    # Components
    s.src  = TestSource( pkt_type, s.src_msgs, s.src_delay )
    s.sink = [TestSink( pkt_type, s.sink_msgs[i], s.sink_delay )
              for i in range( s.num_ports ) ]
    s.dut  = RouteUnitDOR( pkt_type, dimension )
    
    # Dump vcd file
    if dump_vcd:
      s.dut.vcd_file = dump_vcd

    # Translation
    if test_verilog:
      s.dut = TranslationTool( s.dut )

    # Connections
    s.connect( s.dut.pos_x, pos_x     )
    s.connect( s.dut.pos_y, pos_y     )
    s.connect( s.src.out,   s.dut.in_ )
    for i in range( s.num_ports ):
      s.connect( s.dut.out[i], s.sink[i].in_ )

  def done( s ):
    done_flag = s.src.done
    for i in range( s.num_ports ):
      done_flag &= s.sink[i].done
    return done_flag
  
  # TODO: implement line trace
  def line_trace( s ):
    return s.dut.line_trace()

#=======================================================================
# Helper functions
#=======================================================================
NORTH = 0
SOUTH = 1
WEST  = 2
EAST  = 3
SELF  = 4

def run_ru_test( pkt_type, pos_x, pos_y, dimension,
                 test_msgs, src_delay, sink_delay, 
                 dump_vcd=False, test_verilog=False ):
  max_cycles = 100

  src_msgs  = test_msgs[0]
  sink_msgs = test_msgs[1]

  model = TestHarness( pkt_type, pos_x, pos_y, dimension,
                     src_msgs, sink_msgs, src_delay, sink_delay, 
                     dump_vcd, test_verilog )
  model.vcd_file = dump_vcd
  model.test_verilog = test_verilog
  model.elaborate()

  # Run simulation
  sim = SimulationTool( model )
  print ""
  print "="*72
  sim.reset()
  while not model.done() and sim.ncycles < max_cycles:
    sim.eval_combinational()
    sim.print_line_trace()
    sim.cycle()

  # A few extra cycles 
  sim.cycle()
  sim.cycle()
  sim.cycle()

  if not model.done():
    raise AssertionError( "Simulation did not complete in %d cycles!" 
                          % max_cycles )

#empty_pkt = SinglePhitPacket( 
#  src_x_nbits   = 4,
#  src_y_nbits   = 4, 
#  dst_x_nbits   = 4,
#  dst_y_nbits   = 4, 
#  opaque_nbits  = 8,
#  payload_nbits = 32 )
empty_pkt = SinglePhitPacket( 4, 4, 4, 4, 8, 32 )

def mk_pkt( src_x, src_y, dst_x, dst_y, opaque, payload ):
  pkt = copy.deepcopy( empty_pkt ) 
  pkt.src_x   = src_x
  pkt.src_y   = src_y
  pkt.dst_x   = dst_x
  pkt.dst_y   = dst_y
  pkt.opaque  = opaque
  pkt.payload = payload
  return pkt

def mk_test_msgs( num_ports, msg_list ):
  src_msgs  = []
  sink_msgs = [ [] for _ in range( num_ports ) ]
  
  for m in msg_list:
    tsink, src_x, src_y, dst_x, dst_y, opaque, payload = \
    m[0],  m[1],  m[2],  m[3],  m[4],  m[5],   m[6]
    pkt = mk_pkt( src_x,  src_y, dst_x, dst_y, opaque, payload )
    src_msgs.append ( pkt )
    sink_msgs[tsink].append( pkt )

  return [ src_msgs, sink_msgs ]

def dimension_order_routing( dimension, pos_x, pos_y, 
                             src_x, src_y, dest_x, dest_y ):
  tsrc  = 0
  tsink = 0
  north = 0
  south = 1
  west  = 2
  east  = 3
  inout = 4
  # determine source port
  if src_x == pos_x and src_y == pos_y:
    tsrc = inout
  
  elif dimension == 'y':
    if src_x == pos_x:
      if src_y < pos_y:
        tsrc = west
      else:
        tsrc = east
    elif src_x < pos_x:
      tsrc = north
    else:
      tsrc = west
  
  elif dimension == 'x':
    if src_y == pos_y:
      if src_x < pos_x:
        tsrc = north 
      else: 
        tsrc = south
    elif src_y > pos_y:
      tsrc = east
    else:
      tsrc = west 
  else: 
    raise AssertionError( "Invalid dimension input for DOR! " )
  # determine dest port
  if dest_x == pos_x and dest_y == pos_y:
    tsink = inout
  elif dimension == 'y':
    if dest_y > pos_y:
      tsink = east
    elif dest_y < pos_y:
      tsink = west
    elif dest_x > pos_x:
      tsink = south
    else:
      tsink = north
  elif dimension == 'x':
    if dest_x > pos_x:
      tsink = south
    elif dest_x < pos_x:
      tsink = north
    elif dest_y > pos_y:
      tsink = east
    else:
      tsink = west 
  else:
    raise AssertionError( "Invalid dimension input for DOR! " )
  return (tsrc, tsink)

def copmute_sink( pos_x, pos_y, dimension, msg_list ):
  """
  Compute the corresponding test sink that the packet should go to.
  """
  test_list = []
  tsink = 0

  for m in msg_list:
    if dimension.lower() != 'x' and dimension.lower() != 'y':
      raise AssertionError ("[copmute_sink]: Invalid routing algorithm!")

    _, tsink = dimension_order_routing( dimension, pos_x, pos_y,
                                           m[0], m[1], m[2], m[3] )
    print ("{} for {}:({},{}>({},{}))".format(tsink, m[4], m[2], m[3], m[0], m[1]))
    test_list.append( ( tsink, m[0], m[1], m[2], m[3], m[4], m[5] ) )
  return test_list

# NOT USED
def run_ru_tv_test( dump_vcd, test_verilog, 
                  pkt_type, dimension, pos_x, pos_y, test_vectors ):
  """
  A helper function that runs the tests for a given DOR route unit.
  """

  # Elaborate the model
  dut = RouteUnitDOR( empty_pkt, 'x' )
  dut.vcd_file = dump_vcd
  dut = TranslationTool ( dut ) if test_verilog else dut
  dut.elaborate()

  dut.pos_x.value = pos_x
  dut.pos_y.value = pos_y

  # Define input and check functions to the testvector simulator
  def tv_in( dut, test_vector ):
    pass 

  def tv_out( dut, test_vector ):
    pass

  # Run the test
  sim = TestVectorSimulator( dut, tv_in, tv_out )
  sim.run_test()

#=======================================================================
# Directed tests
#=======================================================================

def basic_msgs( pos_x, pos_y, dimension ):
  return mk_test_msgs( 5, copmute_sink( pos_x, pos_y, dimension, [
    # src_x src_y dst_x dst_y opaque payload
    ( 0,    0,    0,    0,    0,     0xdeadd00d ),
    ( 0,    0,    1,    1,    1,     0xdeadcafe ),
  ] ) )

#=======================================================================
# Directed tests
#=======================================================================

test_case_table = mk_test_case_table( [ 
  (                "msg_func    dimension pos_x pos_y src_delay sink_delay" ),
  [ "DOR_y_1pkt",   basic_msgs, 'y',      0,    0,    0,        0           ],
  [ "DOR_x_1pkt",   basic_msgs, 'x',      0,    0,    0,        0           ],
] )

#=======================================================================
# Run tests
#=======================================================================

@pytest.mark.parametrize( **test_case_table )
def test_direct( test_params, dump_vcd, test_verilog ):
  msgs = test_params.msg_func( test_params.pos_x, test_params.pos_y, 
                               test_params.dimension )
  run_ru_test( empty_pkt, test_params.pos_x, test_params.pos_y, 
               test_params.dimension, msgs, 
               test_params.src_delay, test_params.sink_delay,
               dump_vcd, test_verilog )