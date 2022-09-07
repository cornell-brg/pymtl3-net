'''
==========================================================================
XbarRouteUnitMflitRTL.py
==========================================================================
Route unit for crossbar that supports multi-flit packet.

- NOTE:

It requires no tail flit and that the header flit should have a field that
indicates the length of the payload in terms of number of flits.

Authour : Yanghui Ou
   Date : Feb 18, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc

from pymtl3_net.ocnlib.rtl import Counter
from pymtl3_net.ocnlib.utils import get_plen_type
from pymtl3_net.ocnlib.utils.connects import connect_bitstruct

class XbarRouteUnitMflitRTL( Component ):

  #-----------------------------------------------------------------------
  # construct
  #-----------------------------------------------------------------------

  def construct( s, HeaderFormat, num_outports=4, plen_field_name='plen' ):
    # Local parameters
    s.num_outports = num_outports
    s.HeaderFormat = HeaderFormat
    s.PhitType     = mk_bits( HeaderFormat.nbits )
    dir_nbits      = clog2( num_outports ) if num_outports > 1 else 1
    DirType        = mk_bits( dir_nbits )
    PLenType       = get_plen_type( HeaderFormat )
    s.STATE_HEADER = b1(0)
    s.STATE_BODY   = b1(1)

    # Interface
    s.recv = IStreamIfc( s.PhitType )

    s.send = [ OStreamIfc( s.PhitType ) for _ in range( s.num_outports ) ]
    s.hold = [ OutPort( Bits1 ) for _ in range( s.num_outports ) ]

    # Components
    s.header      = Wire( HeaderFormat )
    s.state       = Wire()
    s.state_next  = Wire()
    s.out_dir_r   = Wire( dir_nbits )
    s.out_dir     = Wire( dir_nbits )
    s.any_send_xfer = Wire()

    s.counter = Counter( PLenType )
    s.counter.incr //= 0
    s.counter.load_value //= s.header.plen

    @update
    def up_header():
      s.header @= s.recv.msg

    for i in range( s.num_outports ):
      s.recv.msg //= s.send[i].msg
    s.recv.rdy //= lambda: s.send[ s.out_dir ].rdy

    @update
    def up_any_send_xfer():
      s.any_send_xfer @= 0
      for i in range( s.num_outports ):
        if s.send[i].val & s.send[i].rdy:
          s.any_send_xfer @= 1

    # State transition logic
    @update_ff
    def up_state_r():
      if s.reset:
        s.state <<= s.STATE_HEADER
      else:
        s.state <<= s.state_next

    @update
    def up_state_next():
      s.state_next @= s.state
      if s.state == s.STATE_HEADER:
        # If the packet has body flits
        if s.any_send_xfer & ( s.header.plen > 0 ):
          s.state_next @= s.STATE_BODY

      else: # STATE_BODY
        if ( s.counter.count == 1 ) & s.any_send_xfer:
          s.state_next @= s.STATE_HEADER

    # State output logic
    @update
    def up_counter_decr():
      if s.state == s.STATE_HEADER:
        s.counter.decr @= 0
      else:
        s.counter.decr @= s.any_send_xfer

    @update
    def up_counter_load():
      if s.state == s.STATE_HEADER:
        s.counter.load @= ( s.state_next == s.STATE_BODY )
      else:
        s.counter.load @= 0

    # Routing logic
    # TODO: Figure out how to encode dest id
    @update
    def up_out_dir():
      if ( s.state == s.STATE_HEADER ) & s.recv.val:
        s.out_dir @= s.header.dst[0:dir_nbits]
      else:
        s.out_dir @= s.out_dir_r

    @update_ff
    def up_out_dir_r():
      s.out_dir_r <<= s.out_dir

    @update
    def up_send_val_hold():
      for i in range( s.num_outports ):
        s.send[i].val @= ( i == s.out_dir ) & s.recv.val
        s.hold[i]     @= ( i == s.out_dir ) & ( s.state == s.STATE_BODY )

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    send_trace = '|'.join([ f'{ifc}' for ifc in s.send ])
    hold  = ''.join([ '^' if h else '.' for h in s.hold ])
    count = f'{s.counter.count}'
    state = 'H' if s.state == s.STATE_HEADER else \
            'B' if s.state == s.STATE_BODY else   \
            '!'
    dir   = f'{s.out_dir}'
    return f'{s.recv}([{state}{count}]{dir}{hold}){send_trace}'
