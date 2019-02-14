from pymtl import *

class Encoder( Model ):
  """
  A priority encoder.
  """
  def __init__( s, in_width, out_width ):

    # Interface
    s.in_ =  InPort( in_width  )
    s.out = OutPort( out_width )
    
    # Constants
    s.din_wid  = in_width
    s.dout_wid = out_width

    # Logic
    @s.combinational
    def encode():
      s.out.value = 0
      for i in range( in_width ):
        s.out.value = i if s.in_[i] else s.out
  
  def line_trace( s ):
    return "in:{:0>{n}b} | out:{}".format( int( s.in_ ), s.out, n=s.din_wid ) 
