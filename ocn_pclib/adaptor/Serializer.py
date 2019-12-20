#-------------------------------------------------------------------------------
# Serializer
#-------------------------------------------------------------------------------
from pymtl3 import *
from .PitonNetMsg import *
from pymtl3.stdlib.ifcs import InValRdyIfc, OutValRdyIfc

class Serializer( Component ):
  def construct( s, din_type=mk_piton_net_msg(), dout_type=mk_piton_net_msg_hdr() ):
    s.in_ =  InValRdyIfc( din_type  )
    s.out = OutValRdyIfc( dout_type )

    nlines        = 2

    option_nbits  = 6
    tag_nbits     = 8
    type_nbits    = 8
    len_nbits     = 8
    f_nbits       = 4
    ypos_nbits    = 8
    xpos_nbits    = 8
    chip_id_nbits = 14
    payload_nbits = 64*1

    s.cnt        = Wire( Bits8         )
    s.state      = Wire( Bits2         )
    s.next_state = Wire( Bits2         )
    s.in_wire    = Wire( din_type  )
    s.shreg      = [ Wire( Bits64 ) for _ in range( nlines ) ]

    # state encoding
    s.IDLE = Bits2( 0 )
    s.SEND = Bits2( 1 )
    s.TAIL = Bits2( 2 )

    @s.update
    def assignWires():
      s.in_wire = s.in_.msg
      s.out.val = ( s.state==s.SEND or s.state==s.TAIL )
      s.in_.rdy = ( s.state==s.IDLE or ( s.state==s.TAIL and s.out.rdy ) )
      s.out.msg = s.shreg[0]

    # Next state logic

    @s.update_ff
    def nextStateLogic():
      if s.state == s.IDLE:
        if s.in_.val and s.in_.msg.pay_len > 0:
          s.next_state <<= s.SEND
        elif s.in_.val and s.in_.msg.pay_len == 0:
          s.next_state <<= s.TAIL
        else:
          s.next_state <<= s.IDLE
      #  s.next_state.value = s.SEND if s.in_.val and s.in_.msg.pay_len > 0 s.IDLE
      #else: # s.state == s.SEND
      #  s.next_state.value = s.IDLE if s.cnt==0 else s.SEND
      elif s.state == s.SEND:
        if s.out.rdy and s.cnt == Bits4(2):
          s.next_state <<= s.TAIL
        else:
          s.next_state <<= s.SEND
      else: # s.state == s.TAIL
        # Bypass IDLE state
        if s.in_.val and s.out.rdy and s.in_.msg.pay_len > 0:
          s.next_state <<= s.SEND
        elif (not s.in_.val) and s.out.rdy:
          s.next_state <<= s.IDLE
        else:
          s.next_state <<= s.TAIL
    # FSM logic

    @s.update_ff
    def fsm():
      if s.reset:
        s.state   <<= s.IDLE
        s.cnt     <<= 0
        for i in range( nlines ):
          s.shreg[i] <<= 0
      else:
        s.state <<= s.next_state
        if s.state == s.IDLE:
          if s.in_.val:
            s.cnt <<= s.in_.msg.pay_len + 1
            s.shreg[0] <<= Bits64(
                                   s.in_wire.option   < 58 &\
                                   s.in_wire.tag      < 50 &\
                                   s.in_wire.msg_type < 42 &\
                                   s.in_wire.pay_len  < 34 &\
                                   s.in_wire.fbits    < 30 &\
                                   s.in_wire.ypos     < 22 &\
                                   s.in_wire.xpos     < 14 &\
                                   s.in_wire.chip_id
                                 )
            s.shreg[1] <<= Bits64( s.in_wire.payload )
#            for i in range( nlines ):
#              s.shreg[i] <<= s.in_wire[i*64:i*64+64]

        elif s.state == s.SEND:
          if s.out.val and s.out.rdy:
            s.cnt <<= s.cnt - 1
            s.shreg[nlines-1] <<= 0
            for i in range(nlines-1):
              s.shreg[i] <<= s.shreg[i+1]

        else: # s.state == s.TAIL
          if s.next_state == s.IDLE:
            s.cnt <<= s.cnt - 1
            s.shreg[nlines-1] <<= 0
            for i in range(nlines-1):
              s.shreg[i] <<= s.shreg[i+1]
          elif s.next_state == s.SEND:
            s.cnt <<= s.in_.msg.pay_len + 1
            s.shreg[0] <<= Bits64(
                                   s.in_wire.option   < 58 &\
                                   s.in_wire.tag      < 50 &\
                                   s.in_wire.msg_type < 42 &\
                                   s.in_wire.pay_len  < 34 &\
                                   s.in_wire.fbits    < 30 &\
                                   s.in_wire.ypos     < 22 &\
                                   s.in_wire.xpos     < 14 &\
                                   s.in_wire.chip_id
                                 )
            s.shreg[1] <<= Bits64( s.in_wire.payload )

#            for i in range( nlines ):
#              s.shreg[i] <<= s.in_wire[i*64:i*64+64]
          elif s.next_state == s.TAIL and s.in_.val and s.out.rdy:
            s.cnt <<= s.in_.msg.pay_len + 1
            s.shreg[0] <<= Bits64(
                                   s.in_wire.option   < 58 &\
                                   s.in_wire.tag      < 50 &\
                                   s.in_wire.msg_type < 42 &\
                                   s.in_wire.pay_len  < 34 &\
                                   s.in_wire.fbits    < 30 &\
                                   s.in_wire.ypos     < 22 &\
                                   s.in_wire.xpos     < 14 &\
                                   s.in_wire.chip_id
                                 )
            s.shreg[1] <<= Bits64( s.in_wire.payload )

#            for i in range( nlines ):
#              s.shreg[i] <<= s.in_wire[i*64:i*64+64]

  def line_trace( s ):
    state_str = "I" if s.state == s.IDLE else "S" if s.state == s.SEND else "T"
    return "ser_state:{}, cnt:{}, in_val:{}, in_rdy:{}, out_val:{}, out_rdy:{}, out_msg:{}".format(
            state_str, s.cnt, s.in_.val, s.in_.rdy, s.out.val, s.out.rdy, s.out.msg )
