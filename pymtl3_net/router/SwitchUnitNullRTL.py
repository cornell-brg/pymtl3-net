'''
==========================================================================
SwitchUnitNullRTL.py
==========================================================================
A null switch unit that is used for single input router.

Author : Yanghui Ou
  Date : Feb 21, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc

class SwitchUnitNullRTL( Component ):

  def construct( s, Type, num_inports=1 ):

    assert num_inports == 1, 'Null switch unit can only be used for single-input router!'

    # Interface

    s.recv = [ IStreamIfc( Type ) for _ in range( num_inports )  ]
    s.hold = [ InPort() for _ in range( num_inports ) ]
    s.send = OStreamIfc( Type )

    connect( s.send, s.recv[0] )

  def line_trace( s ):
    in_trace  = '|'.join( [ str(p) for p in s.recv ] )
    hold      = ''.join([ '^' if h else '.' for h in s.hold ])
    out_trace = f'{s.send}'
    return f'{in_trace}({hold}){out_trace}'
