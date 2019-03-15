from pymtl import *

class SinglePhitPacket( BitStructDefinition ):
  """
  A single phit packet that may or may not have source/destination fields.
  """
  def __init__( s, src_x_nbits, src_y_nbits, dst_x_nbits, dst_y_nbits, 
                opaque_nbits, payload_nbits ):
    # Source field 
    if not ( src_x_nbits <= 0 and src_y_nbits <= 0 ):
      if src_x_nbits <= 0:
        s.src = BitField( src_y_nbits )
      elif src_y_nbits <= 0:
        s.src = BitField( src_x_nbits )
      else:
        s.src_x = BitField( src_x_nbits )
        s.src_y = BitField( src_y_nbits )

    # Destination field
    if not ( dst_x_nbits <= 0 and dst_y_nbits <= 0 ):
      if dst_x_nbits <= 0:
        s.dst = BitField( dst_y_nbits )
      elif dst_y_nbits <= 0:
        s.dst = BitField( dst_x_nbits )
      else:
        s.dst_x = BitField( dst_x_nbits )
        s.dst_y = BitField( dst_y_nbits )
    
    s.opaque  = BitField( opaque_nbits  )
    s.payload = BitField( payload_nbits )

  # TODO: Implement better __str__ funtion.
  def __str__( s ):
    return "{}:({},{})>({},{})".format( 
      s.opaque, s.src_x, s.src_y, s.dst_x, s.dst_y )

