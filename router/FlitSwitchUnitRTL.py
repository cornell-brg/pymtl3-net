"""
=========================================================================
FlitSwitchUnitRTL.py
=========================================================================
Flit-based switch unit.

Author : Cheng Tan
  Date : July 19, 2019
"""
from pymtl3 import *
from pymtl3.stdlib.rtl import Mux
from pymtl3.stdlib.rtl.arbiters import RoundRobinArbiterEn
from pymtl3.stdlib.rtl.Encoder import Encoder
from pymtl3.stdlib.ifcs import GetIfcRTL, SendIfcRTL, GiveIfcRTL

class FlitSwitchUnitRTL( Component ):

  def construct( s, PacketType, num_inports=5 ):

    # Local parameters

    s.num_inports = num_inports
    s.sel_width   = clog2( num_inports )
    GrantType     = mk_bits( num_inports )
    SelType       = mk_bits( s.sel_width )
    s.set_ocp = 0
    s.clear_ocp = 0

    # Interface

    s.get  = [ GetIfcRTL( PacketType ) for _ in range( s.num_inports ) ]
    s.give = GiveIfcRTL( PacketType )
    s.out_ocp = OutPort( Bits1 )

    # Components

    s.get_en  = [ Wire( Bits1 ) for _ in range( s.num_inports ) ]
    s.get_rdy = [ Wire( Bits1 ) for _ in range( s.num_inports ) ]

    s.arbiter = RoundRobinArbiterEn( num_inports )( en=b1(1) )
    s.mux = Mux( PacketType, num_inports )( out = s.give.msg )

    s.encoder = Encoder( num_inports, s.sel_width )(
      in_ = s.arbiter.grants,
      out = s.mux.sel
    )

    # Connections

    for i in range( num_inports ):
      s.connect( s.get[i].rdy, s.arbiter.reqs[i] )
      s.connect( s.get[i].msg, s.mux.in_[i]      )
      s.connect( s.get[i].en,  s.get_en[i]       )
      s.connect( s.get[i].rdy, s.get_rdy[i]      )

    @s.update
    def up_give():
      s.give.rdy = s.arbiter.grants > GrantType(0)

    @s.update
    def up_get_en():
      for i in range( num_inports ):
        s.get_en[i] = s.give.en & ( s.mux.sel==SelType(i) )
        if s.get_en[i] == 1 and s.get[i].msg.fl_type == 0:
          s.set_ocp = 1
        elif s.get_en[i] == 1 and (s.get[i].msg.fl_type==2 or s.get[i].msg.fl_type==3): 
          s.clear_ocp = 1
 
    @s.update_on_edge
    def set_occupy():
      if s.set_ocp == 1:
        s.out_ocp = 1
        s.set_ocp = 0
      if s.clear_ocp == 1:
        s.out_ocp = 0
        s.clear_ocp = 0

#      if s.give.en and s.get[i].msg.fl_type == 0:
#        s.out_ocp = 1
#        print 'Switch Pos({}) set ocp=1 msg={}'.format(s.pos, s.get[i].msg)
#      elif s.give.en and (s.get[i].msg.fl_type==2 or s.get[i].msg.fl_type==3):
#        s.out_ocp = 0
#        print 'Switch Pos({}) set ocp=0 msg={}'.format(s.pos, s.get[i].msg)
 
  # Line trace

  def line_trace( s ):
    in_trace = [ str(s.get[i]) for i in range( s.num_inports ) ]
    return "{}(){}".format( "|".join( in_trace ), s.give )
