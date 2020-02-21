'''
==========================================================================
SwitchUnitNullRTL.py
==========================================================================
A null switch unit that is used for single input router.

Author : Yanghui Ou
  Date : Feb 21, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs import GetIfcRTL, GiveIfcRTL

class SwitchUnitNullRTL( Component ):

  def construct( s, Type, num_inports=1 ):

    assert num_inports == 1, 'Null switch unit can only be used for single-input router!'

    # Interface

    s.get  = [ GetIfcRTL( Type ) for _ in range( num_inports )  ]
    s.hold = [ InPort( Bits1 ) for _ in range( num_inports ) ]
    s.give = GiveIfcRTL( Type )

    # connect( s.give.en,  s.get[0].en  )
    # connect( s.give.ret, s.get[0].ret )
    # connect( s.give.rdy, s.get[0].rdy )

    connect( s.give, s.get[0] )

  def line_trace( s ):
    in_trace  = '|'.join( [ str(p) for p in s.get ] )
    hold      = ''.join([ '^' if h else '.' for h in s.hold ])
    out_trace = f'{s.give}'
    return f'{in_trace}({hold}){out_trace}'
