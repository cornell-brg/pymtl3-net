"""
==========================================================================
OutputUnitRTL.py
==========================================================================
RTL implementation of OutputUnit with val/rdy stream interface.

Author : Yanghui Ou, Cheng Tan
  Date : Feb 28, 2019
"""
from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc
from pymtl3.stdlib.stream import StreamNormalQueue


class OutputUnitRTL( Component ):
  def construct( s, PacketType, QueueType=None ):

    # Local parameter
    # gating_out = PacketType()
    # TODO: add data gating support

    # Interface
    s.recv = IStreamIfc( PacketType )
    s.send = OStreamIfc( PacketType )

    s.QueueType = QueueType

    #---------------------------------------------------------------------
    # If no queue type is assigned
    #---------------------------------------------------------------------

    if s.QueueType != None:

      # Component
      s.queue = QueueType( PacketType )

      # Connections
      s.recv       //= s.queue.recv
      s.queue.send //= s.send

    #---------------------------------------------------------------------
    # No ouput queue
    #---------------------------------------------------------------------

    else:

      s.send //= s.recv

  def line_trace( s ):
    if s.QueueType != None:
      return "{}({}){}".format( s.recv, s.queue.count, s.send )
    else:
      return "{}(0){}".format( s.recv, s.send)

