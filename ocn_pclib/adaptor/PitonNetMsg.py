"""
==========================================================================
PitonNetMsg.py
==========================================================================
Collection of Piton Net Message definition.

Author : Cheng Tan
  Date : Dec 17, 2019
"""

from pymtl3 import *

#-------------------------------------------------------------------------------
# Piton Message Header
#-------------------------------------------------------------------------------

def mk_piton_net_msg_hdr( option_nbits   = 6,
                          tag_nbits      = 8,
                          type_nbits     = 8,
                          len_nbits      = 8,
                          f_nbits        = 4,
                          ypos_nbits     = 8,
                          xpos_nbits     = 8,
                          chip_id_nbits  = 14,
                          prefix="PitonNetMsgHdr"
                        ):

  new_name = f"{prefix}"

  def str_func( s ):
    return "id:{},xpos:{},ypos:{},fbits:{},len:{},type:{},tag:{},opt:{}".format(
      s.chip_id, s.xpos, s.ypos, s.fbits, s.pay_len, s.msg_type, s.tag, s.option )

  return mk_bitstruct( new_name, {
      #s.nbits    = 64
      'chip_id'  : mk_bits( chip_id_nbits ),
      'xpos'     : mk_bits( xpos_nbits    ),
      'ypos'     : mk_bits( ypos_nbits    ),
      'fbits'    : mk_bits( f_nbits       ),
      'pay_len'  : mk_bits( len_nbits     ),
      'msg_type' : mk_bits( type_nbits    ),
      'tag'      : mk_bits( tag_nbits     ),
      'option'   : mk_bits( option_nbits  ),
    },
    namespace = { '__str__': str_func }
  )

#class PitonNetMsgHdr( BitStructDefinition ):
#	def __init__( s,
#		option_nbits   = 6,
#		tag_nbits      = 8,
#		type_nbits     = 8,
#		len_nbits      = 8,
#		f_nbits        = 4,
#		ypos_nbits     = 8,
#		xpos_nbits     = 8,
#		chip_id_nbits  = 14):
#
#		#s.nbits    = 64
#		s.chip_id  = BitField( chip_id_nbits )
#		s.xpos     = BitField( xpos_nbits    )
#		s.ypos     = BitField( ypos_nbits    )
#		s.fbits    = BitField( f_nbits       )
#		s.pay_len  = BitField( len_nbits     )
#		s.msg_type = BitField( type_nbits    )
#		s.tag      = BitField( tag_nbits     )
#		s.option   = BitField( option_nbits  )
#
#	def __str__( s ):
#		return "id:{},xpos:{},ypos:{},fbits:{},len:{},type:{},tag:{},opt:{}".format(
#			    s.chip_id, s.xpos, s.ypos, s.fbits, s.pay_len, s.msg_type, s.tag, s.option )

#-------------------------------------------------------------------------------
# PitonNetMsg
#-------------------------------------------------------------------------------

def mk_piton_net_msg( option_nbits   = 6,
                      tag_nbits      = 8,
                      type_nbits     = 8,
                      len_nbits      = 8,
                      f_nbits        = 4,
                      ypos_nbits     = 8,
                      xpos_nbits     = 8,
                      chip_id_nbits  = 14,
                      payload_nbits  = 64*1,
                      # FIXME: AssertionError: We don't allow bitwidth to exceed 512.
                      # payload_nbits  = 64*11,
                      prefix="PitonNetMsg"
                    ):

  new_name = f"{prefix}"


  def str_func( s ):
    payload_str = s.payload.__str__()
    payload_str = payload_str.lstrip( "0" )
    return "id:{},xpos:{},ypos:{},fbits:{},len:{},type:{},tag:{},opt:{},payload:{}".format(
      s.chip_id, s.xpos, s.ypos, s.fbits, s.pay_len, s.msg_type, s.tag, s.option, payload_str )

  return mk_bitstruct( new_name, {
      #s.nbits    = 64
      'payload'  : mk_bits( payload_nbits ),
      'chip_id'  : mk_bits( chip_id_nbits ),
      'xpos'     : mk_bits( xpos_nbits    ),
      'ypos'     : mk_bits( ypos_nbits    ),
      'fbits'    : mk_bits( f_nbits       ),
      'pay_len'  : mk_bits( len_nbits     ),
      'msg_type' : mk_bits( type_nbits    ),
      'tag'      : mk_bits( tag_nbits     ),
      'option'   : mk_bits( option_nbits  ),
    },
    namespace = { '__str__': str_func }
  )

#class PitonNetMsg( BitStructDefinition ):
#	def __init__( s,
#		option_nbits   = 6,
#		tag_nbits      = 8,
#		type_nbits     = 8,
#		len_nbits      = 8,
#		f_nbits        = 4,
#		ypos_nbits     = 8,
#		xpos_nbits     = 8,
#		chip_id_nbits  = 14,
#		payload_nbits  = 64*11 ):
#
#		#s.nbits    = 64*12
#		s.payload  = BitField( payload_nbits )
#		s.chip_id  = BitField( chip_id_nbits )
#		s.xpos     = BitField( xpos_nbits    )
#		s.ypos     = BitField( ypos_nbits    )
#		s.fbits    = BitField( f_nbits       )
#		s.pay_len  = BitField( len_nbits     )
#		s.msg_type = BitField( type_nbits    )
#		s.tag      = BitField( tag_nbits     )
#		s.option   = BitField( option_nbits  )
#
#	def __str__( s ):
#		# Remove leading 0s for better readability
#		payload_str = s.payload.__str__()
#		payload_str = payload_str.lstrip( "0" )
#		return "id:{},xpos:{},ypos:{},fbits:{},len:{},type:{},tag:{},opt:{},payload:{}".format(
#			    s.chip_id, s.xpos, s.ypos, s.fbits, s.pay_len, s.msg_type, s.tag, s.option, payload_str )

def mk_piton_msg( payload, chip_id, xpos, ypos, fbits, pay_len, msg_type, tag, option ):
#  msg = PitonNetMsg()
  PitonMsgType = mk_piton_net_msg()
  msg = PitonMsgType( payload, chip_id, xpos, ypos, fbits, pay_len, msg_type, tag, option )
  return msg

