from pymtl import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.rtl import Mux, RoundRobinArbiterEn
from pc import Encoder

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
    s.encoder = Encoder( num_inports, sel_width )
    s.mux_msg = Mux( msg_type, num_inports )
    s.mux_val = Mux( 1,        num_inports )

    # Connections
    s.connect( s.arbiter.grants, s.encoder.in_ )
    s.connect( s.encoder.out,    s.mux_msg.sel )
    s.connect( s.encoder.out,    s.mux_val.sel )
    s.connect( s.mux_val.out,    s.out.val     )
    s.connect( s.mux_msg.out,    s.out.msg     )

    for i in range( num_inports ):
      s.connect( s.in_[i].msg, s.mux_msg.in_[i] )
      s.connect( s.in_[i].val, s.mux_val.in_[i] )

    @s.combinational
    def inRdy():
      for i in range( num_inports ):
        s.in_[i].rdy.value = s.arbiter.grants[i] and s.out.rdy

  # TODO: implement line trace
  def line_trace( s ):
    return ""
