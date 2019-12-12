"""
==========================================================================
SwitchUnitCL.py
==========================================================================
Cycle level implementation of a round robin switch unit.

Author : Yanghui Ou
  Date : May 16, 2019
"""
from pymtl3 import *


class SwitchUnitCL( Component ):

  def construct( s, PacketType, num_inports=5 ):

    # Constants

    s.num_inports = num_inports

    # Interface

    s.get  = [ NonBlockingCallerIfc( PacketType ) for _ in range( s.num_inports ) ]
    s.give.Type = PacketType

    # Components

    s.priority = [ i for i in range( s.num_inports ) ]
    s.msg = None

    for i in range( s.num_inports ):
      s.add_constraints( M( s.get[i] ) == M( s.give ) )

  def any_ready( s ):
    flag = False
    for i in range( s.num_inports ):
      if s.get[i].rdy is not None:
        flag = flag or s.get[i].rdy()
    return flag

  @non_blocking( lambda s: s.any_ready() )
  def give( s ):
    for i in s.priority:
      if s.get[i].rdy():
        s.priority.remove( i )
        s.priority.append( i )
        return s.get[i]()

  # CL line trace

  def line_trace( s ):
    in_str = "|".join([ str(s.get[i]) for i in range(s.num_inports) ])
    return f"{in_str}_({s.priority})_{s.give}"
