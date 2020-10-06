'''
==========================================================================
PitonRouterValRdy.py
==========================================================================
A wrapper around PitonRouter that has val/rdy interfaces.

Author : Yanghui Ou
  Date : Jun 3, 2020
'''
from pymtl3 import *
from pymtl3.passes.backends.verilog import *
from pymtl3.stdlib.ifcs import InValRdyIfc, OutValRdyIfc

from ocnlib.rtl.valrdy_queues import NormalQueueValRdy
from router.InputUnitValRdy import InputUnitValRdy
from router.OutputUnitValRdy import OutputUnitValRdy
from router.SwitchUnitGrantHoldValRdy import SwitchUnitGrantHoldValRdy

from .PitonNoCHeader import PitonNoCHeader
from .PitonRouteUnitValRdy import PitonRouteUnitValRdy

#-------------------------------------------------------------------------
# PitonRouterValRdy
#-------------------------------------------------------------------------

class PitonRouterValRdy( Component ):

  def construct( s,
    PositionType,
    InputUnitType  = InputUnitValRdy,
    RouteUnitType  = PitonRouteUnitValRdy,
    SwitchUnitType = SwitchUnitGrantHoldValRdy,
    OutputUnitType = OutputUnitValRdy,
  ):

    # Local parameter

    s.num_inports  = 5
    s.num_outports = 5
    assert PitonNoCHeader.nbits == 64
    s.PhitType     = Bits64

    # Metadata

    s.set_metadata( VerilogTranslationPass.explicit_module_name, f'pyocn_router' )

    # Interface

    s.in_ = [ InValRdyIfc ( Bits64 ) for _ in range(5) ]
    s.out = [ OutValRdyIfc( Bits64 ) for _ in range(5) ]
    s.pos = InPort( PositionType )

    # Components

    s.input_units  = [ InputUnitType( s.PhitType, QueueType=NormalQueueValRdy )
                       for _ in range( s.num_inports ) ]

    s.route_units  = [ RouteUnitType( PositionType )
                       for i in range( s.num_inports ) ]

    s.switch_units = [ SwitchUnitType( s.PhitType, s.num_inports )
                       for _ in range( s.num_outports ) ]

    s.output_units = [ OutputUnitType( s.PhitType )
                       for _ in range( s.num_outports ) ]

    # Connections

    for i in range( s.num_inports ):
      s.in_[i]             //= s.input_units[i].in_
      s.input_units[i].out //= s.route_units[i].in_
      s.pos                //= s.route_units[i].pos

    for i in range( s.num_inports ):
      for j in range( s.num_outports ):
        s.route_units[i].out[j] //= s.switch_units[j].in_[i]
        s.route_units[i].hold[j] //= s.switch_units[j].hold[i]

    for j in range( s.num_outports ):
      s.switch_units[j].out //= s.output_units[j].in_
      s.output_units[j].out //= s.out[j]

  #-----------------------------------------------------------------------
  # Line trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    in_trace  = '|'.join([ f'{ifc}' for ifc in s.in_ ])
    out_trace = '|'.join([ f'{ifc}' for ifc in s.out ])
    return f'{in_trace}({s.pos}){out_trace}'
