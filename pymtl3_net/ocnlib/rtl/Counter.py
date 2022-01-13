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

    s.incr       = InPort ()
    s.decr       = InPort ()
    s.load       = InPort ()
    s.load_value = InPort ( Type )
    s.count      = OutPort( Type )

    # Logic

    @update_ff
    def up_count():

      if s.reset:
        s.count <<= reset_value

      elif s.load:
        s.count <<= s.load_value

      elif s.incr & ~s.decr:
        s.count <<= s.count + 1

      elif ~s.incr & s.decr:
        s.count <<= s.count - 1

  def line_trace( s ):
    return f"{s.count}"
