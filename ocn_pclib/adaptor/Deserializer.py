#-----------------------------------------------------------
# Deerilizer
#-----------------------------------------------------------

from pymtl3 import *
from .PitonNetMsg import *
from pymtl3.stdlib.ifcs import InValRdyIfc, OutValRdyIfc
# TODO: rewrite fsm in a cleaner manner
class Deserializer( Component ):
  def construct( s ):
    # constants
    msg_type_in   = mk_piton_net_msg_hdr()
    msg_type_out  = mk_piton_net_msg()
    dwidth        = 64
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

    lenType = mk_bits( len_nbits )
    s.in_ =  InValRdyIfc( msg_type_in   )
    s.out = OutValRdyIfc( msg_type_out  )
    s.cnt          = Wire( Bits8        )
    s.out_reg      = Wire( msg_type_out )
    s.state        = Wire( Bits2        )
    # A register file that stores all the flits
    widthType = mk_bits( dwidth )
    s.out_reg_wire = [ Wire( widthType ) for _ in range( nlines ) ]
    s.wr_addr      = Wire( Bits4 )
#    for i in range( nlines ):
    current_pos = 0
    next_pos = 64
    s.out_reg_wire[0][current_pos:next_pos] //= s.out_reg.payload
    current_pos = 0
    next_pos = chip_id_nbits
    print("next_pos: ", next_pos)
    s.out_reg_wire[1][current_pos:next_pos] //= s.out_reg.chip_id
    current_pos = next_pos
    next_pos = next_pos + xpos_nbits
    s.out_reg_wire[1][current_pos:next_pos] //= s.out_reg.xpos
    current_pos = next_pos
    next_pos = next_pos + ypos_nbits
    s.out_reg_wire[1][current_pos:next_pos] //= s.out_reg.ypos
    current_pos = next_pos
    next_pos = next_pos + f_nbits
    s.out_reg_wire[1][current_pos:next_pos] //= s.out_reg.fbits
    current_pos = next_pos
    next_pos = next_pos + len_nbits
    s.out_reg_wire[1][current_pos:next_pos] //= s.out_reg.pay_len
    current_pos = next_pos
    next_pos = next_pos + type_nbits
    s.out_reg_wire[1][current_pos:next_pos] //= s.out_reg.msg_type
    current_pos = next_pos
    next_pos = next_pos + tag_nbits
    s.out_reg_wire[1][current_pos:next_pos] //= s.out_reg.tag
    current_pos = next_pos
    next_pos = next_pos + option_nbits
    s.out_reg_wire[1][current_pos:next_pos] //= s.out_reg.option

#      s.connect_wire(src=s.out_reg_wire[i], dest=s.out_reg[i*64:(i+1)*64])

    s.IDLE = Bits2( 0 )
    s.RECV = Bits2( 0 )
    s.SEND = Bits2( 0 )

    @s.update_ff
    def fsm():
      if s.reset:
        s.state   <<= s.IDLE
        s.cnt     <<= Bits8( 0 )
        s.wr_addr <<= Bits4( 0 )
        #s.out_reg.next = 0
        for i in range( nlines ):
          s.out_reg_wire[i] <<= widthType( 0 )

      elif s.state == s.IDLE:
        if s.in_.val and s.in_.msg.pay_len > lenType( 0 ):
          s.state           <<= s.RECV
          s.cnt             <<= s.in_.msg.pay_len
          s.wr_addr <<= Bits4( 1 )
          s.out_reg_wire[0] <<= s.in_.msg
          #s.out_reg[0:64].next = s.in_.msg
        elif s.in_.val and s.in_.msg.pay_len == lenType( 0 ):
          s.state <<= s.SEND
          s.cnt <<= s.in_.msg.pay_len
          s.wr_addr         <<= Bits4( 1 )
          s.out_reg_wire[0] <<= s.in_.msg
        else:
          s.state   <<= s.IDLE
          s.cnt     <<= Bits8( 0 )
          #s.out_reg.next = 0

      elif s.state == s.RECV:
        if s.cnt==Bits8(0) or ( s.cnt==Bits8(1) and s.in_.val and s.in_.rdy ):
        #if s.cnt==0:
          s.state   <<= s.SEND
          s.cnt     <<= 0
          s.wr_addr <<= 0
          s.out_reg_wire[s.wr_addr] <<= s.in_.msg
          #s.out_reg.next = s.out_reg
        elif s.in_.val:
          # shift out reg
          #s.out_reg_wire[1].next = s.in_.msg
          #s.out_reg[64:128].next = s.in_.msg
          s.out_reg_wire[s.wr_addr] <<= s.in_.msg
          #for i in range( 2, 12 ):
          #  s.out_reg[i*64:i*64+64].next = s.out_reg[(i-1)*64:(i-1)*64+64]
          s.cnt <<= s.cnt - 1
          s.wr_addr <<= s.wr_addr + 1
        else:
          s.state   <<= s.state
          #s.out_reg.next = s.out_reg
          s.cnt     <<= s.cnt
          s.wr_addr <<= s.wr_addr

      else: # SEND
        if s.out.val and s.out.rdy:
          s.state   <<= s.IDLE
          #s.out_reg.next = 0
          s.cnt     <<= 0
          s.wr_addr <<= 0
          for i in range( nlines ):
            s.out_reg_wire[i] <<= 0
        else:
          s.state <<= s.state
          #s.out_reg.next = s.out_reg

    @s.update
    def outVal():
      s.out.val = 1 if s.state==s.SEND else 0
      s.in_.rdy = 1 if s.state!=s.SEND else 0
      s.out.msg = s.out_reg

  def line_trace( s ):
    state_str = "I" if s.state == s.IDLE else "R" if s.state == s.RECV else "S"
    return "des_state:{}, cnt:{}, in_val{}, in_rdy:{} ,out_val:{}, out_rdy:{}, out_msg:{}".format(
            state_str, s.cnt, s.in_.val, s.in_.rdy, s.out.val, s.out.rdy, s.out.msg )
