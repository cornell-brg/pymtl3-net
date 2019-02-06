from pymtl import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.rtl  import RoundRobinArbiterEn

class GrantHoldArbiter( Model ):
  """
  A round robin arbiter with hold logic.
  """

  def __init__( s, nreqs ):

    # Interface
    s.reqs   = InPort ( nreqs )
    s.grants = OutPort( nreqs )
    s.hold   = InPort ( 1 )

    # Constants
    s.nreqs = nreqs

    # Components 
    s.arb        = RoundRobinArbiterEn( nreqs )
    s.last       = Wire( nreqs )
    s.arb_en     = Wire( 1     )
    # s.grants_out = Wire( nreqs )

    # Connections
    s.connect( s.arb_en, s.arb.en )

    # Logic
    @s.tick_rtl
    def registerGrants():
      s.last.next = s.grants

    @s.combinational
    def assignGrant():
      s.arb.reqs.value = 0 if s.hold else s.reqs 
      s.arb.en.value   = not s.hold
      s.grants.value   = s.arb.grants if not s.hold else s.last

  def line_trace( s ):
    return (
      "reqs:{:0>{n}b} ->| hold:{:b}, last:{:0>{n}b} |-> "
      "grants:{:0>{n}b}".format( 
        int( s.reqs ), int( s.hold ), int( s.last ), int( s.grants ), 
        n=s.nreqs ) ) 
