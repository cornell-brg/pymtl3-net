#=========================================================================
# MeshRouterRTL.py
#=========================================================================

from pymtl      import *
from pclib.ifcs import NetMsg
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.rtl  import NormalQueue, Crossbar
from pclib.rtl  import RoundRobinArbiterEn
from MeshNetMsg import MeshNetMsg
#from RouterDpathPRTL import RouterDpathPRTL
#from RouterCtrlPRTL  import RouterCtrlPRTL

class MeshVCRouterRTL( Model ):
  def __init__ ( s, 
                 opaque_nbits  = 8,
                 payload_nbits = 32, 
                 mesh_wid      = 2,
                 mesh_ht       = 2,
                 routing_algo  = 'DOR_Y',
                 virtual_channel = 'false'
                ):
    #-------------------------------------------------------------
    # Parameters & Constants
    #-------------------------------------------------------------

    num_ports = 5
    msg_type   = MeshNetMsg( mesh_wid, mesh_ht, opaque_nbits, payload_nbits)
    sel_nbits  = clog2 ( num_ports )
    x_addr_nbits = clog2 ( mesh_wid )
    y_addr_nbits = clog2 ( mesh_ht  )

    s.x_addr_nbits  = x_addr_nbits
    s.y_addr_nbits  = y_addr_nbits
    s.opaque_nbits  = opaque_nbits
    s.payload_nbits = payload_nbits

    s.opaque_offset = s.payload_nbits
    s.src_y_offset  = s.opaque_offset + s.opaque_nbits
    s.src_x_offset  = s.src_y_offset  + s.y_addr_nbits
    s.dest_y_offset = s.src_x_offset  + s.x_addr_nbits
    s.dest_x_offset = s.dest_y_offset + s.y_addr_nbits
    s.last_bit      = s.dest_x_offset + s.x_addr_nbits 


    # TODO : Make sure this is correct 
    x_dest_offset = y_addr_nbits+x_addr_nbits+y_addr_nbits+opaque_nbits+payload_nbits
    y_dest_offset = x_addr_nbits+y_addr_nbits+opaque_nbits+payload_nbits
    # routing directions 1 for north, 2 for east, etc
    DIR_W = 0
    DIR_N = 1
    DIR_E = 2
    DIR_S = 3
    DIR_C = 4
    #-------------------------------------------------------------
    # Interface
    #-------------------------------------------------------------
    s.in_       = InValRdyBundle [num_ports]( msg_type )
    s.out       = OutValRdyBundle[num_ports]( msg_type )

    # This might not be useful anymore
    #s.router_id = InPort( addr_nbits )

    s.pos_x     = InPort( x_addr_nbits )
    s.pos_y     = InPort( y_addr_nbits )

    #-------------------------------------------------------------
    # Components
    #-------------------------------------------------------------
    
    # Signals
    s.sels   = Wire[num_ports]( sel_nbits  )
    s.dest_x = Wire[num_ports]( x_addr_nbits )
    s.dest_y = Wire[num_ports]( y_addr_nbits )

    s.arbitor_en = Wire( num_ports )
    s.has_grant  = Wire( num_ports )

    # Crossbar -- no output buffers
    s.crossbar = m = Crossbar(num_ports, msg_type)
    for i in range( num_ports ):
      s.connect( m.out[i], s.out[i].msg )
      s.connect_wire( dest=m.sel[i], src=s.sels[i])

    # Input buffers
    if virtual_channel:
      s.vc_id      = Wire[num_ports]( 1 )
      s.vc_out_id  = Wire[num_ports]( 1 )
      s.vc_arb_en  = Wire[num_ports]( 1 )
      s.vc_out_val = Wire[num_ports]( 1 )
      s.vc_out_rdy = Wire[num_ports]( 1 )
      s.vc_out_msg = Wire[num_ports]( s.last_bit )
      # Virtual channel buffers - 
      #   upper buffer reserved for X DOR and lower for Y DOR
      s.vc_buffers_upper = NormalQueue[num_ports](2, msg_type)
      s.vc_buffers_lower = NormalQueue[num_ports](2, msg_type)
      for i in range( num_ports ):
        s.connect_pairs(
          s.vc_buffers_upper[i].enq.msg, s.in_[i].msg,
          s.vc_buffers_lower[i].enq.msg, s.in_[i].msg
        )
      s.vc_arbitor_en = Wire[num_ports](2)
      s.vc_arbitors   = RoundRobinArbiterEn[num_ports](2)
      for i in range( num_ports ):
        s.connect_pairs(
          s.vc_buffers_upper[i].deq.val, s.vc_arbitors[i].reqs[0],
          s.vc_buffers_lower[i].deq.val, s.vc_arbitors[i].reqs[1],
          s.vc_arb_en[i],                s.vc_arbitors[i].en
        )
    else:
      # Normal Input buffers
      s.input_buffer = NormalQueue[num_ports](2, msg_type)
      for i in range( num_ports ):
        s.connect_pairs(
          s.input_buffer[i].enq.msg,     s.in_[i].msg,
          s.input_buffer[i].deq.msg, s.crossbar.in_[i]
        )
      @s.combinational
      def normalOut():
        for i in ( num_ports ):
          s.vc_out_msg[i].value = s.input_buffer[i].deq.msg
          s.vc_out_val[i].value = s.input_buffer[i].deq.val
          s.input_buffer[i].deq.rdy = s.vc_out_rdy[i]

    # Virtual channel connections
    if virtual_channel:
      @s.combinational
      def vcInValRdy():
          for i in range( num_ports ):
            # DeMux the val signal
            s.vc_buffers_upper[i].enq.val.value = s.in_[i].val if s.vc_id[i] == 0 else 0
            s.vc_buffers_lower[i].enq.val.value = s.in_[i].val if s.vc_id[i] == 1 else 0
            # Mux the rdy signal
            if s.vc_id[i] == 0:
              s.in_[i].rdy.value = s.vc_buffers_upper[i].enq.rdy
            else:
              s.in_[i].rdy.value = s.vc_buffers_lower[i].enq.rdy

      @s.combinational
      def vcOutValRdy():
        for i in range( num_ports ):
          # DeMux rdy signal
          s.vc_buffers_upper[i].deq.rdy.value = s.vc_out_rdy[i] if s.vc_out_id[i] == 0 else 0
          s.vc_buffers_lower[i].deq.rdy.value = s.vc_out_rdy[i] if s.vc_out_id[i] == 1 else 0
          # Mux msg and val
          if s.vc_out_id[i] == 0:
            s.vc_out_val[i].value = s.vc_buffers_upper[i].deq.val
            s.vc_out_msg[i].value = s.vc_buffers_upper[i].deq.msg
          else:
            s.vc_out_val[i].value = s.vc_buffers_lower[i].deq.val
            s.vc_out_msg[i].value = s.vc_buffers_lower[i].deq.msg

      for i in range( num_ports ):
        s.connect( s.vc_out_msg[i], s.crossbar.in_[i] )

    # Arbitors for each output port
    s.arbitors = RoundRobinArbiterEn[num_ports](num_ports)
    for i in range( num_ports ):
      s.connect_pairs( 
        s.arbitors[i].en, s.arbitor_en[i] 
      )

    #--------------------------------------------------------------
    # Control Logic
    #--------------------------------------------------------------
    if virtual_channel:
      @s.combinational
      def setVCInID():
        for i in range( num_ports ):
          s.vc_id[i].value = s.in_[i].msg[s.opaque_offset]

      @s.combinational
      def setVCOutID():
        for i in range( num_ports ):
          if s.vc_arbitors[i].grants[0]:
            s.vc_out_id[i].value = 0
          else:
            s.vc_out_id[i].value = 1

    @s.combinational
    def getDestAddr():
      for i in range( num_ports ):
        s.dest_x[i].value = s.vc_out_msg[i][x_dest_offset:x_dest_offset+x_addr_nbits]
        s.dest_y[i].value = s.vc_out_msg[i][y_dest_offset:y_dest_offset+y_addr_nbits]

    @s.combinational
    def setCrossbarSel():
      for i in range( num_ports ):
        for j in range( num_ports ):
          if s.arbitors[i].grants[j]:
            s.sels[i].value = j

    @s.combinational
    def setOutVal():
      for i in range( num_ports ):
        s.out[i].val.value = 0
        if s.arbitors[i].grants > 0 :
          s.out[i].val.value = 1


    @s.combinational
    def setDeqRdy():
      for i in range( num_ports ):
        s.has_grant[i].value = 0        
        for j in range( num_ports ):
          if s.arbitors[j].grants[i]:
            s.has_grant[i].value = s.out[j].rdy

      for i in range( num_ports ):
        s.vc_out_rdy[i].value = s.has_grant[i] 

    @s.combinational
    def setArbitorEnable():
      for i in range( num_ports ):
        s.arbitor_en[i].value = s.out[i].val & s.out[i].rdy 
    
    # Routing Algorithm
    # y-dimension-order routing
    if routing_algo == 'DOR_Y':
      @s.combinational
      def yDORSetArbitorReq():
          for i in range( num_ports ):
            s.arbitors[i].reqs.value = 0
          for i in range( num_ports ):
            if s.pos_x == s.dest_x[i] and s.pos_y == s.dest_y[i]:
              s.arbitors[DIR_C].reqs[i].value = s.vc_out_val[i]

            elif s.dest_y[i] < s.pos_y:
              s.arbitors[DIR_N].reqs[i].value = s.vc_out_val[i]
            
            elif s.dest_y[i] > s.pos_y:
              s.arbitors[DIR_S].reqs[i].value = s.vc_out_val[i]
            
            elif s.dest_x[i] < s.pos_x:
              s.arbitors[DIR_W].reqs[i].value = s.vc_out_val[i]
            
            else:
              s.arbitors[DIR_E].reqs[i].value = s.vc_out_val[i]

    elif routing_algo == 'DOR_X':
      @s.combinational
      def xDORSetArbitorReq():
        for i in range( num_ports ):
          s.arbitors[i].reqs.value = 0
        for i in range( num_ports ):
          if s.pos_x == s.dest_x[i] and s.pos_y == s.dest_y[i]:
            s.arbitors[DIR_C].reqs[i].value = s.vc_out_val[i]

          elif s.dest_x[i] < s.pos_x:
            s.arbitors[DIR_W].reqs[i].value = s.vc_out_val[i]
          
          elif s.dest_x[i] > s.pos_x:
            s.arbitors[DIR_E].reqs[i].value = s.vc_out_val[i]
          
          elif s.dest_y[i] < s.pos_y:
            s.arbitors[DIR_N].reqs[i].value = s.vc_out_val[i]
          
          else:
            s.arbitors[DIR_S].reqs[i].value = s.vc_out_val[i]
    # TODO: set 
    elif routing_algo == 'O1Turn':
      @s.combinational
      def o1turnSetArbitorReq():
        for i in range( num_ports ):
          s.arbitors[i].reqs.value = 0
        for i in range( num_ports ):
          # 0 for y-DOR
          if vc_id[i] == 0:
            for i in range( num_ports ):
              if s.pos_x == s.dest_x[i] and s.pos_y == s.dest_y[i]:
                s.arbitors[DIR_C].reqs[i].value = s.vc_out_val[i]

              elif s.dest_y[i] < s.pos_y:
                s.arbitors[DIR_N].reqs[i].value = s.vc_out_val[i]
              
              elif s.dest_y[i] > s.pos_y:
                s.arbitors[DIR_S].reqs[i].value = s.vc_out_val[i]
              
              elif s.dest_x[i] < s.pos_x:
                s.arbitors[DIR_W].reqs[i].value = s.vc_out_val[i]
              
              else:
                s.arbitors[DIR_E].reqs[i].value = s.vc_out_val[i]
          else:
            for i in range( num_ports ):
              if s.pos_x == s.dest_x[i] and s.pos_y == s.dest_y[i]:
                s.arbitors[DIR_C].reqs[i].value = s.vc_out_val[i]

              elif s.dest_x[i] < s.pos_x:
                s.arbitors[DIR_W].reqs[i].value = s.vc_out_val[i]
              
              elif s.dest_x[i] > s.pos_x:
                s.arbitors[DIR_E].reqs[i].value = s.vc_out_val[i]
              
              elif s.dest_y[i] < s.pos_y:
                s.arbitors[DIR_N].reqs[i].value = s.vc_out_val[i]
              
              else:
                s.arbitors[DIR_S].reqs[i].value = s.vc_out_val[i]                       
    else:
      raise AssertionError( 'Invalid routing algorithm!' )
    
  def line_trace( s ):
    opaque_offset = s.payload_nbits
    opaque_slice = slice( s.opaque_offset, s.src_y_offset  )
    src_y_slice  = slice( s.src_y_offset,  s.src_x_offset  )     
    src_x_slice  = slice( s.src_x_offset,  s.dest_y_offset )   
    dest_y_slice = slice( s.dest_y_offset, s.dest_x_offset )   
    dest_x_slice = slice( s.dest_x_offset, s.last_bit      )  
    in_str = [ "" for _ in range(5) ]
    for i in range(5):
      in_str[i] = s.in_[i].to_str( "%02s:(%1s,%1s)>(%1s,%1s)" % 
                                  ( s.in_[i].msg.opaque, 
                                    s.in_[i].msg.src_x,  s.in_[i].msg.src_y, 
                                    s.in_[i].msg.dest_x, s.in_[i].msg.dest_y ) )
    return "({},{})({}|{}|{}|{}|{})".format( s.pos_x, s.pos_y, 
                                              in_str[0], in_str[1], in_str[2], in_str[3], in_str[4]  )  
