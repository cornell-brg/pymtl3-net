'''
==========================================================================
XbarRouteUnitRTL
==========================================================================
Route unit for single-flit xbar.

Author : Yanghui Ou
  Date : Apr 16, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc

class XbarRouteUnitRTL( Component ):

  def construct( s, PacketType, num_outports ):

    # Local parameters

    dir_nbits = 1 if num_outports==1 else clog2( num_outports )
    DirT      = mk_bits( dir_nbits )
    BitsN     = mk_bits( num_outports )

    # Interface

    s.recv = IStreamIfc( PacketType )
    s.send = [ OStreamIfc( PacketType ) for _ in range( num_outports ) ]

    # Componets

    s.out_dir  = Wire( DirT  )
    s.send_val = Wire( BitsN )

    # Connections

    for i in range( num_outports ):
      s.recv.msg    //= s.send[i].msg
      s.send_val[i] //= s.send[i].val

    # Routing logic

    @update
    def up_ru_routing():
      s.out_dir @= trunc( s.recv.msg.dst, dir_nbits )

      for i in range( num_outports ):
        s.send[i].val @= b1(0)

      if s.recv.val:
        s.send[ s.out_dir ].val @= b1(1)

    @update
    def up_ru_recv_rdy():
      s.recv.rdy @= s.send[ s.out_dir ].rdy > 0

  # Line trace
  def line_trace( s ):
    out_str = "|".join([ str(x) for x in s.send ])
    return f"{s.recv}({s.out_dir}){out_str}"
