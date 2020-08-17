'''
==========================================================================
TorusTile.py
==========================================================================
Author : Yanghui Ou
  Date : Aug 12, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.basic_rtl import Reg

from ocnlib.ifcs.CreditIfc import CreditRecvIfcRTL, CreditSendIfcRTL
from ocnlib.rtl.DummyCore import DummyCore
from channel.BidirectionalChannelCreditRTL import BidirectionalChannelCreditRTL as Channel

from ..TorusISlipRouterRTL import TorusISlipRouterRTL
from ..directions import *

class TorusTile( Component ):

  def construct( s, PacketType, PositionType, credit_line=2, latency=0 ):

    # Local parameter

    PhitType = mk_bits( PacketType.nbits )

    # Interface

    s.recv = [ CreditRecvIfcRTL( PhitType, vc=2 ) for _ in range(4) ]
    s.send = [ CreditSendIfcRTL( PhitType, vc=2 ) for _ in range(4) ]

    s.feedthru_recv = [ CreditRecvIfcRTL( PhitType, vc=2 ) for _ in range(4) ]
    s.feedthru_send = [ CreditSendIfcRTL( PhitType, vc=2 ) for _ in range(4) ]


    s.pos  = InPort( PositionType )

    # Component

    s.core   = DummyCore( PhitType )
    s.router = TorusISlipRouterRTL( PacketType, PositionType,
                               credit_line=credit_line, ncols=16, nrows=16 )
    s.pos_reg = Reg( PositionType )

    s.channel_ns = Channel( PhitType, latency=[latency,latency] )
    s.channel_we = Channel( PhitType, latency=[latency,latency] )

    # Connections

    s.pos //= s.pos_reg.in_
    s.pos_reg.out //= s.router.pos

    s.router.send[NORTH] //= s.channel_ns.recv[0]
    s.channel_ns.send[0] //= s.send[NORTH]
    s.router.recv[NORTH] //= s.channel_ns.send[1]
    s.channel_ns.recv[1] //= s.recv[NORTH]

    s.router.send[SOUTH] //= s.send[SOUTH]
    s.router.recv[SOUTH] //= s.recv[SOUTH]

    s.router.send[EAST] //= s.channel_we.recv[0]
    s.channel_we.send[0] //= s.send[EAST]
    s.router.recv[EAST] //= s.channel_we.send[1]
    s.channel_we.recv[1] //= s.recv[EAST]

    s.router.send[WEST] //= s.send[WEST]
    s.router.recv[WEST] //= s.recv[WEST]

    # Hacky connection
    s.router.send[SELF].msg    //= s.core.recv.msg
    s.router.send[SELF].en     //= s.core.recv.en
    s.router.send[SELF].yum[0] //= s.core.recv.rdy
    s.router.send[SELF].yum[1] //= s.core.recv.rdy

    s.router.recv[SELF].msg    //= s.core.send.msg
    s.router.recv[SELF].en     //= s.core.send.en
    s.router.recv[SELF].yum[0] //= s.core.send.rdy
    # s.router.recv[SELF].yum[1] //= s.core.send.rdy

    s.feedthru_recv[NORTH] //= s.feedthru_send[SOUTH]
    s.feedthru_recv[SOUTH] //= s.feedthru_send[NORTH]
    s.feedthru_recv[WEST]  //= s.feedthru_send[EAST]
    s.feedthru_recv[EAST]  //= s.feedthru_send[WEST]

  def line_trace( s ):
    return s.router.line_trace()

