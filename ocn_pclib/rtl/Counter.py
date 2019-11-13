"""
==========================================================================
 Counter.py
==========================================================================
A simple counter implementation.

Author : Yanghui Ou
  Date : June 13, 2019
"""

from pymtl3 import *

class Counter( Component ):

  def construct( s, Type, reset_value=0 ):

    # Interface

    s.incr       = InPort ( Bits1 )
    s.decr       = InPort ( Bits1 )
    s.load       = InPort ( Bits1 )
    s.load_value = InPort ( Type  )
    s.count      = OutPort( Type  )

    # Logic

    @s.update_ff
    def up_count():

      if s.reset:
        s.count <<= Type( reset_value )

      elif s.load:
        s.count <<= s.load_value

      elif s.incr & ~s.decr:
        s.count <<= s.count + Type(1)

      elif ~s.incr & s.decr:
        s.count <<= s.count - Type(1)

  def line_trace( s ):
    return "{}".format( s.count )
