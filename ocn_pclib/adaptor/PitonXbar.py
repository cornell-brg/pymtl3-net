#-------------------------------------------------------------------------------
# PitonXBar
#-------------------------------------------------------------------------------
from pymtl3             import *
from .PitonNetMsg       import *
from pymtl3.stdlib.ifcs import InValRdyIfc, OutValRdyIfc
from pymtl3.stdlib.rtl.queues import NormalQueueRTL
from pymtl3.stdlib.rtl  import Crossbar
from pymtl3.stdlib.rtl  import RoundRobinArbiterEn, RoundRobinArbiter
from .Serializer        import Serializer
from .Deserializer      import Deserializer

class PitonXbar ( Component ):

  def construct( s,
                 num_ports=3,
                 hdr_type=mk_piton_net_msg_hdr(),
                 msg_type=mk_piton_net_msg() ):

    # Constants

    s.num_ports = num_ports
    sel_nbits  = clog2 ( num_ports )

    # Interface

    s.in_ = [ InValRdyIfc( hdr_type ) for _ in range( num_ports ) ]
    s.out = [ OutValRdyIfc( hdr_type ) for _ in range( num_ports ) ]

    # Component

    s.des      = [ Deserializer() for _ in range( num_ports ) ]
    s.xbar     = Crossbar( num_ports, msg_type )
    s.ser      = [ Serializer() for _ in range( num_ports ) ]

    s.arbitors = [ RoundRobinArbiterEn( num_ports ) for _ in range( num_ports ) ]

    # Wires

    s.sels        = [ Wire( mk_bits(sel_nbits) ) for _ in range( num_ports ) ]
    s.arb_en      = [ Wire( Bits1 )     for _ in range( num_ports ) ]
    s.has_grant   = [ Wire( Bits1 )     for _ in range( num_ports ) ]
    s.ser_in_val  = [ Wire( Bits1 )     for _ in range( num_ports ) ]
    s.ser_in_rdy  = [ Wire( Bits1 )     for _ in range( num_ports ) ]
    s.des_out_val = [ Wire( Bits1 )     for _ in range( num_ports ) ]
    s.des_out_rdy = [ Wire( Bits1 )     for _ in range( num_ports ) ]
    s.des_out_msg = [ Wire( msg_type )  for _ in range( num_ports ) ]
    s.offchip     = [ Wire( Bits1 )     for _ in range( num_ports ) ]
    s.dest_x      = [ Wire( Bits8 )     for _ in range( num_ports ) ]

    # Datapath

    for i in range( num_ports ):
      connect( s.in_[i],          s.des[i].in_      )
      connect( s.des[i].out.msg,  s.xbar.in_[i]     )
      connect( s.xbar.out[i],     s.ser[i].in_.msg  )
      connect( s.ser[i].out,      s.out[i]          )

    # Control

    for i in range( num_ports ):
      connect( s.sels[i],        s.xbar.sel[i]     )
      connect( s.arb_en[i],      s.arbitors[i].en  )
      connect( s.des[i].out.msg, s.des_out_msg[i]  )
      connect( s.des[i].out.val, s.des_out_val[i]  )
      connect( s.des_out_rdy[i], s.des[i].out.rdy  )
      connect( s.ser_in_val[i],  s.ser[i].in_.val  )
      connect( s.ser[i].in_.rdy, s.ser_in_rdy[i]   )

    @s.update
    def xbarSel():
      for i in range( num_ports ):
        for j in range( num_ports ):
          if s.arbitors[i].grants[j]:
            s.sels[i] = j

    @s.update
    def offchipSet():
      for i in range( num_ports ):
        s.offchip[i] = s.des_out_msg[i].chip_id[13]
        # s.offchip[i] = s.des_out_msg[i][63]

    @s.update
    def desOutRdy():
      for i in range( num_ports ):
        s.has_grant[i] = 0
        for j in range( num_ports ):
          if s.arbitors[j].grants[i]:
            s.has_grant[i] = s.ser_in_rdy[j]

      for i in range( num_ports ):
        s.des_out_rdy[i] = s.has_grant[i]

    @s.update
    def serInVal():
      for i in range( num_ports ):
        s.ser_in_val[i] = 0
        if s.arbitors[i].grants > 0 :
          s.ser_in_val[i] = 1
        #print ( "s.ser_in_val[%d] = %d" % ( i, s.ser_in_val[i] ) )

    @s.update
    def arbitorEnable():
      for i in range( num_ports ):
        s.arb_en[i] = s.ser_in_val[i] & s.ser_in_rdy[i]

    @s.update
    def arbitorReq():
      for i in range( num_ports ):
        for j in range( num_ports ):
          s.arbitors[i].reqs[j] = 0

      #for i in range( num_ports ):
      #  s.arbitors[i].reqs.value = 0
      #  s.dest_x[i].value = ( num_ports - 1 ) if s.offchip[i] \
      #                                        else s.des_out_msg[i].xpos
      #  for j in range( num_ports ):
      #    if s.dest_x[i] == j:
      #      s.arbitors[j].reqs[i].value = s.des_out_val[i]

        #s.arbitors[s.dest_x[i]].reqs[i].value = s.des_out_val[i]

      for i in range( num_ports ):
        s.dest_x[i] = s.des_out_msg[i].xpos
        # s.dest_x[i] = s.des_out_msg[i][42:50]
        if s.offchip[i]:
          s.arbitors[num_ports-1].reqs[i] = s.des_out_val[i]
        else:
          s.arbitors[s.dest_x[i]].reqs[i] = s.des_out_val[i]

        #print( "dest_x[%d] = %d" % ( i, s.dest_x[i] )  )
        #print( "arbitors[%d].reqs[0] = %d" % ( i, s.arbitors[1].reqs[0].value ) )
        #print( "arbitors[%d].reqs[1] = %d" % ( i, s.arbitors[1].reqs[1].value ) )
        #print( "arbitors[%d].grants[0] = %d" % ( i, s.arbitors[1].grants[0].value ) )
        #print( "arbitors[%d].grants[1] = %d" % ( i, s.arbitors[1].grants[1].value ) )
        #print( "sels[%d] = %d" % ( i, s.sels[i] ) )

  def line_trace( s ):
    inp_trace = [ "" for _ in range( s.num_ports ) ]
    arb_trace = [ "" for _ in range( s.num_ports ) ]
    out_trace = [ "" for _ in range( s.num_ports ) ]
    trace     = "xbar trace:\n"
    for i in range( s.num_ports ):
      inp_trace[i] = "  in_[{}]: val:{}, rdy:{}, dest:{}, msg:{} \n".format(
                      i,  s.des_out_val[i], s.des_out_rdy[i],
                      s.dest_x[i], s.des_out_msg[i] )
      inp_trace[i] += "  " + s.des[i].line_trace() + "\n"

      arb_trace[i] = s.arbitors[i].line_trace()

      out_trace[i] = "  out[{}]: val:{}, rdy:{}, msg:{} \n".format(
                      i,  s.ser_in_val[i], s.ser_in_rdy[i], s.ser[i].in_.msg )
      out_trace[i] += "  " + s.ser[i].line_trace() + "\n"
      trace += inp_trace[i]
    trace += "\n"
    for i in range( s.num_ports ):
      trace += ( "  arb[%d]: " % i )
      trace += ( arb_trace[i] + "\n" )
    trace += "\n"
    for i in range( s.num_ports ):
      trace += out_trace[i]

    return trace
