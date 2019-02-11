from pymtl import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle

class SwitchUnit( Model ):
  """
  A switch unit implementing round-robin arbitration.
  """
  def __init__( s, msg_type, dimension ):

    # Constants 
    s.num_inports = 5
    NORTH = 0
    SOUTH = 1
    WEST  = 2
    EAST  = 3
    SELF  = 4

    # Interface
    s.in_ =  InValRdyBundle[ s.num_inports ]( msg_type )
    s.out = OutValRdyBundle( msg_type )

    # Componets
#    s.in_rdys = Wire( s.num_outports )
    s.count_arbitor = Wire( Bits(8) ) # arbitrating in round-robin (increment in every tick)

    # Connections
#    for i in range( s.num_outports ):
#      s.connect( s.in_[i].msg,       s.out[i].msg )
#      s.connect( s.in_rdys[i],   s.in_[i].rdy )
    
    @s.combinational
    def assignInRdy():
      s.in_[s.count_arbitor].rdy.value = Bits(8, 0)

    # Switch logic
    @s.tick
    def switchLogic():
      s.out.val.next = s.in_[s.count_arbitor].val
      if s.reset:
        s.count_arbitor.next = 0
      else:
        if s.count_arbitor == SELF:
          s.count_arbitor.next = 0
        else:
          s.count_arbitor.next = s.count_arbitor + 1


  def line_trace( s ):
    return "{} {}".format( s.count_arbitor, s.out.val)
