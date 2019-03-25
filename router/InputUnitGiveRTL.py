#=========================================================================
# InputUnitGiveRTL.py
#=========================================================================
# An input unit with a recv interface as input and give interface as 
# output.
#
# Author : Yanghui Ou
#   Date : Mar 23, 2019

from pymtl import *
from pclib.ifcs           import RecvIfcRTL
from ocn_pclib.ifcs       import GiveIfcRTL
from ocn_pclib.rtl.queues import NormalQueueRTL

class InputUnitGiveRTL( RTLComponent ):

  def construct( s, PacketType, QueueType=NormalQueueRTL ):

    # Interface

    s.recv = RecvIfcRTL( PacketType )
    s.send = GiveIfcRTL( PacketType )

    # Component

    s.queue = QueueType( PacketType )
    
    # Connections

    s.connect( s.recv,      s.queue.enq )
    s.connect( s.queue.deq, s.send      )

  def line_trace( s ):
    return "{}({}){}".format( s.recv, s.queue.credit, s.send )
