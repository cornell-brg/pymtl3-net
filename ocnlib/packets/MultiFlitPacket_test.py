'''
==========================================================================
MultiFlitPacket_test.py
==========================================================================
Unit tests for MultiFlitPacket.

Author : Yanghui Ou
  Date : Jan 31, 2019
'''
from pymtl3 import *

from .packet_formats import packet_format
from .MultiFlitPacket import MultiFlitPacket

@bitstruct
class SimpleFormat:
  opaque : Bits8
  src    : Bits8
  dst    : Bits8
  plen   : Bits8

def test_add():
  # An empty packet
  pkt = MultiFlitPacket( SimpleFormat )
  assert pkt.empty()

  header      = b32(0) 
  header[0:8] = b8(3)
  pkt.add( header )
  pkt.add( b32(0xdeadbeef) )
  assert not pkt.empty()
  pkt.add( b32(0xfaceb00c) )
  assert not pkt.empty()
  pkt.add( b32(0xfeedbabe) )
  assert not pkt.empty()

  assert pkt.full()
  assert pkt.flits[1] == 0xdeadbeef
  assert pkt.flits[2] == 0xfaceb00c
  assert pkt.flits[3] == 0xfeedbabe

def test_pop():
  # A single-flit packet
  header = b32(0)
  pkt    = MultiFlitPacket( SimpleFormat, [ header ] )
  assert not pkt.empty()
  assert pkt.full()
  assert pkt.pop() == b32(0)
  assert pkt.empty()
  assert not pkt.full()

  # A multi-flit packet
  header      = b32(0)
  header[0:8] = b8(2)
  flits       = [ header, b32(0xfaceb00c), b32(0x8badf00d) ]
  pkt         = MultiFlitPacket( SimpleFormat, flits )

  assert not pkt.empty()
  assert pkt.full()

  assert pkt.pop() == b32(2)
  assert not pkt.full()
  assert not pkt.empty()

  assert pkt.pop() == b32(0xfaceb00c)
  assert not pkt.full()
  assert not pkt.empty()

  assert pkt.pop() == b32(0x8badf00d)
  assert not pkt.full()
  assert pkt.empty()
