from pymtl import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.rtl import Mux, RoundRobinArbiterEn
from pc.Encoder import Encoder

class SwitchUnit( Model ):
  """
  A simple switch unit that supports single-phit packet.
  """
  def __init__( s, msg_type, num_inports ):

    # Constants
    s.num_inports = num_inports
    s.sel_width   = clog2( num_inports )

    # Interface
    s.in_ =  InValRdyBundle[ s.num_inports ]( msg_type )
    s.out = OutValRdyBundle( msg_type )

    # Components
    s.arbiter = RoundRobinArbiterEn( num_inports )
    s.encoder = Encoder( num_inports, s.sel_width )
    s.mux = Mux( msg_type, num_inports )

    # Connections
    s.connect( s.arbiter.grants, s.encoder.in_ )
    s.connect( s.encoder.out,    s.mux.sel     )
    s.connect( s.mux.out,        s.out.msg     )

    for i in range( num_inports ):
      s.connect( s.in_[i].msg, s.mux.in_[i]      )
      s.connect( s.in_[i].val, s.arbiter.reqs[i] )

    @s.combinational
    def inRdy():
      for i in range( num_inports ):
        s.in_[i].rdy.value = s.arbiter.grants[i] and s.out.rdy

    @s.combinational
    def enableArbiter():
      s.out.val.value = s.arbiter.grants > 0
      s.arbiter.en.value = (s.arbiter.grants > 0) and s.out.rdy
  
  # TODO: implement line trace
  def line_trace( s ):
    return ""
