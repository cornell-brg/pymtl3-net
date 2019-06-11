typedef struct packed {
  logic [3:0] dst_x;
  logic [3:0] dst_y;
  logic [3:0] opaque;
  logic [15:0] payload;
  logic [3:0] src_x;
  logic [3:0] src_y;
} Packet;

typedef struct packed {
  logic [3:0] pos_x;
  logic [3:0] pos_y;
} MeshPosition_9x9;

module RegisterFile__Type_Packet__nregs_2__rd_ports_1__wr_ports_1__const_zero_False
(
  input logic [0:0] clk,
  input logic [0:0] raddr [0:0],
  output Packet rdata [0:0],
  input logic [0:0] reset,
  input logic [0:0] waddr [0:0],
  input Packet wdata [0:0],
  input logic [0:0] wen [0:0]
);
  localparam [31:0] _fvar_wr_ports = 32'd1;
  localparam [31:0] _fvar_nregs = 32'd2;
  localparam [31:0] _fvar_rd_ports = 32'd1;
  Packet next_regs [0:1];
  Packet regs [0:1];

  // PYMTL SOURCE:
  // 
  // @s.update
  // def up_rf_read():
  //   for i in xrange( rd_ports ):
  //     s.rdata[i] = s.regs[ s.raddr[i] ]
  
  always_comb begin : up_rf_read
    for ( int i = 0; i < _fvar_rd_ports; i += 1 )
      rdata[i] = regs[raddr[i]];
  end

  // PYMTL SOURCE:
  // 
  // @s.update
  // def up_rf_write():
  //   for i in xrange( wr_ports ):
  //     if s.wen[i]:
  //       s.next_regs[ s.waddr[i] ] = s.wdata[i]
  
  always_comb begin : up_rf_write
    for ( int i = 0; i < _fvar_wr_ports; i += 1 )
      if ( wen[i] ) begin
        next_regs[waddr[i]] = wdata[i];
      end
  end

  // PYMTL SOURCE:
  // 
  // @s.update_on_edge
  // def up_rfile():
  //   for i in xrange( nregs ):
  //     s.regs[i] = s.next_regs[i]
  
  always_ff @(posedge clk) begin : up_rfile
    for ( int i = 0; i < _fvar_nregs; i += 1 )
      regs[i] <= next_regs[i];
  end

endmodule


module NormalQueueDpathRTL__MsgType_Packet__num_entries_2
(
  input logic [0:0] clk,
  output Packet deq_msg,
  input Packet enq_msg,
  input logic [0:0] raddr,
  input logic [0:0] reset,
  input logic [0:0] waddr,
  input logic [0:0] wen
);
  logic [0:0] queue$clk;
  logic [0:0] queue$raddr [0:0];
  Packet queue$rdata [0:0];
  logic [0:0] queue$reset;
  logic [0:0] queue$waddr [0:0];
  Packet queue$wdata [0:0];
  logic [0:0] queue$wen [0:0];

  RegisterFile__Type_Packet__nregs_2__rd_ports_1__wr_ports_1__const_zero_False queue (
    .clk( queue$clk ),
    .raddr( queue$raddr ),
    .rdata( queue$rdata ),
    .reset( queue$reset ),
    .waddr( queue$waddr ),
    .wdata( queue$wdata ),
    .wen( queue$wen )
  );

  assign queue$clk = clk;
  assign queue$reset = reset;
  assign queue$raddr[0] = raddr;
  assign queue$waddr[0] = waddr;
  assign queue$wdata[0] = enq_msg;
  assign deq_msg = queue$rdata[0];
  assign queue$wen[0] = wen;

endmodule


module NormalQueueCtrlRTL__num_entries_2
(
  input logic [0:0] clk,
  output logic [1:0] count,
  input logic [0:0] deq_en,
  output logic [0:0] deq_rdy,
  input logic [0:0] enq_en,
  output logic [0:0] enq_rdy,
  output logic [0:0] raddr,
  input logic [0:0] reset,
  output logic [0:0] waddr,
  output logic [0:0] wen
);
  localparam [31:0] last_idx = 32'd1;
  localparam [31:0] num_entries = 32'd2;
  logic [0:0] deq_xfer;
  logic [0:0] enq_xfer;
  logic [0:0] head;
  logic [0:0] head_next;
  logic [0:0] tail;
  logic [0:0] tail_next;

  // PYMTL SOURCE:
  // 
  // @s.update
  // def up_xfer_signals():
  //   s.enq_xfer  = s.enq_en and s.enq_rdy
  //   s.deq_xfer  = s.deq_en and s.deq_rdy
  
  always_comb begin : up_xfer_signals
    enq_xfer = enq_en && enq_rdy;
    deq_xfer = deq_en && deq_rdy;
  end

  // PYMTL SOURCE:
  // 
  // @s.update
  // def up_rdy_signals():
  //   s.enq_rdy = Bits1(Bits32(s.count) < s.num_entries)
  //   s.deq_rdy = s.count > Bits2(0)
  
  always_comb begin : up_rdy_signals
    enq_rdy = 1'( 32'( count ) < num_entries );
    deq_rdy = count > 2'd0;
  end

  // PYMTL SOURCE:
  // 
  // @s.update
  // def up_next():
  //   s.head_next = s.head - Bits1(1) if s.head > Bits1(0) else PtrType( s.last_idx )
  //   s.tail_next = s.tail + Bits1(1) if Bits32(s.tail) < s.last_idx else PtrType(0)
  
  always_comb begin : up_next
    head_next = ( head > 1'd0 ) ? head - 1'd1 : 1'( last_idx );
    tail_next = ( 32'( tail ) < last_idx ) ? tail + 1'd1 : 1'd0;
  end

  // PYMTL SOURCE:
  // 
  // @s.update_on_edge
  // def up_reg():
  // 
  //   if s.reset:
  //     s.head  = PtrType(0)
  //     s.tail  = PtrType(0)
  //     s.count = CountType(0)
  // 
  //   else:
  //     s.head   = s.head_next if s.deq_xfer else s.head
  //     s.tail   = s.tail_next if s.enq_xfer else s.tail
  //     s.count  = s.count + Bits2(1) if s.enq_xfer and not s.deq_xfer else \
  //                s.count - Bits2(1) if s.deq_xfer and not s.enq_xfer else \
  //                s.count
  
  always_ff @(posedge clk) begin : up_reg
    if ( reset ) begin
      head <= 1'd0;
      tail <= 1'd0;
      count <= 2'd0;
    end
    else begin
      head <= deq_xfer ? head_next : head;
      tail <= enq_xfer ? tail_next : tail;
      count <= ( enq_xfer && ( !deq_xfer ) ) ? count + 2'd1 : ( deq_xfer && ( !enq_xfer ) ) ? count - 2'd1 : count;
    end
  end

  assign wen = enq_xfer;
  assign waddr = tail;
  assign raddr = head;

endmodule


module NormalQueueRTL__MsgType_Packet__num_entries_2
(
  input logic [0:0] clk,
  output logic [1:0] count,
  input logic [0:0] reset,
  input logic [0:0] deq_$en,
  output Packet deq_$msg,
  output logic [0:0] deq_$rdy,
  input logic [0:0] enq_$en,
  input Packet enq_$msg,
  output logic [0:0] enq_$rdy
);
  logic [0:0] ctrl$clk;
  logic [1:0] ctrl$count;
  logic [0:0] ctrl$deq_en;
  logic [0:0] ctrl$deq_rdy;
  logic [0:0] ctrl$enq_en;
  logic [0:0] ctrl$enq_rdy;
  logic [0:0] ctrl$raddr;
  logic [0:0] ctrl$reset;
  logic [0:0] ctrl$waddr;
  logic [0:0] ctrl$wen;

  NormalQueueCtrlRTL__num_entries_2 ctrl (
    .clk( ctrl$clk ),
    .count( ctrl$count ),
    .deq_en( ctrl$deq_en ),
    .deq_rdy( ctrl$deq_rdy ),
    .enq_en( ctrl$enq_en ),
    .enq_rdy( ctrl$enq_rdy ),
    .raddr( ctrl$raddr ),
    .reset( ctrl$reset ),
    .waddr( ctrl$waddr ),
    .wen( ctrl$wen )
  );

  logic [0:0] dpath$clk;
  Packet dpath$deq_msg;
  Packet dpath$enq_msg;
  logic [0:0] dpath$raddr;
  logic [0:0] dpath$reset;
  logic [0:0] dpath$waddr;
  logic [0:0] dpath$wen;

  NormalQueueDpathRTL__MsgType_Packet__num_entries_2 dpath (
    .clk( dpath$clk ),
    .deq_msg( dpath$deq_msg ),
    .enq_msg( dpath$enq_msg ),
    .raddr( dpath$raddr ),
    .reset( dpath$reset ),
    .waddr( dpath$waddr ),
    .wen( dpath$wen )
  );

  assign ctrl$clk = clk;
  assign ctrl$reset = reset;
  assign dpath$clk = clk;
  assign dpath$reset = reset;
  assign dpath$wen = ctrl$wen;
  assign dpath$waddr = ctrl$waddr;
  assign dpath$raddr = ctrl$raddr;
  assign ctrl$enq_en = enq_$en;
  assign enq_$rdy = ctrl$enq_rdy;
  assign ctrl$deq_en = deq_$en;
  assign deq_$rdy = ctrl$deq_rdy;
  assign count = ctrl$count;
  assign dpath$enq_msg = enq_$msg;
  assign deq_$msg = dpath$deq_msg;

endmodule


module InputUnitRTL__PacketType_Packet__QueueType_NormalQueueRTL
(
  input logic [0:0] clk,
  input logic [0:0] reset,
  input logic [0:0] give_$en,
  output Packet give_$msg,
  output logic [0:0] give_$rdy,
  input logic [0:0] recv_$en,
  input Packet recv_$msg,
  output logic [0:0] recv_$rdy
);
  logic [0:0] queue$clk;
  logic [1:0] queue$count;
  logic [0:0] queue$reset;
  logic [0:0] queue$deq_$en;
  Packet queue$deq_$msg;
  logic [0:0] queue$deq_$rdy;
  logic [0:0] queue$enq_$en;
  Packet queue$enq_$msg;
  logic [0:0] queue$enq_$rdy;

  NormalQueueRTL__MsgType_Packet__num_entries_2 queue (
    .clk( queue$clk ),
    .count( queue$count ),
    .reset( queue$reset ),
    .deq_$en( queue$deq_$en ),
    .deq_$msg( queue$deq_$msg ),
    .deq_$rdy( queue$deq_$rdy ),
    .enq_$en( queue$enq_$en ),
    .enq_$msg( queue$enq_$msg ),
    .enq_$rdy( queue$enq_$rdy )
  );

  assign queue$clk = clk;
  assign queue$reset = reset;
  assign queue$enq_$en = recv_$en;
  assign queue$enq_$msg = recv_$msg;
  assign recv_$rdy = queue$enq_$rdy;
  assign give_$msg = queue$deq_$msg;
  assign queue$deq_$en = give_$en;
  assign give_$rdy = queue$deq_$rdy;

endmodule


module OutputUnitRTL__PacketType_Packet__QueueType_None
(
  input logic [0:0] clk,
  input logic [0:0] reset,
  input logic [0:0] recv_$en,
  input Packet recv_$msg,
  output logic [0:0] recv_$rdy,
  output logic [0:0] send_$en,
  output Packet send_$msg,
  input logic [0:0] send_$rdy
);

  assign send_$en = recv_$en;
  assign send_$msg = recv_$msg;
  assign recv_$rdy = send_$rdy;

endmodule


module Encoder__in_width_5__out_width_3
(
  input logic [0:0] clk,
  input logic [4:0] in_,
  output logic [2:0] out,
  input logic [0:0] reset
);
  localparam [31:0] din_wid = 32'd5;
  localparam [31:0] dout_wid = 32'd3;
  localparam [31:0] _fvar_in_width = 32'd5;

  // PYMTL SOURCE:
  // 
  // @s.update
  // def encode():
  //   #TODO: need to change the bitwidth for correct translation.
  //   s.out = Bits3(0)
  //   for i in range( in_width ):
  //     s.out = Bits3(i) if s.in_[i] else s.out
  
  always_comb begin : encode
    out = 3'd0;
    for ( int i = 0; i < _fvar_in_width; i += 1 )
      out = in_[i] ? 3'( i ) : out;
  end

endmodule


module RegEnRst__Type_Bits5__reset_value_1
(
  input logic [0:0] clk,
  input logic [0:0] en,
  input logic [4:0] in_,
  output logic [4:0] out,
  input logic [0:0] reset
);
  localparam [31:0] _fvar_reset_value = 32'd1;

  // PYMTL SOURCE:
  // 
  // @s.update_on_edge
  // def up_regenrst():
  //   if s.reset: s.out = Type( reset_value )
  //   elif s.en:  s.out = deepcopy( s.in_ )
  
  always_ff @(posedge clk) begin : up_regenrst
    if ( reset ) begin
      out <= 5'd1;
    end
    else if ( en ) begin
      out <= in_;
    end
  end

endmodule


module RoundRobinArbiterEn__nreqs_5
(
  input logic [0:0] clk,
  input logic [0:0] en,
  output logic [4:0] grants,
  input logic [4:0] reqs,
  input logic [0:0] reset
);
  localparam [31:0] _fvar_nreqs = 32'd5;
  localparam [31:0] _fvar_nreqsX2 = 32'd10;
  logic [9:0] grants_int;
  logic [10:0] kills;
  logic [0:0] priority_en;
  logic [9:0] priority_int;
  logic [9:0] reqs_int;
  logic [0:0] priority_reg$clk;
  logic [0:0] priority_reg$en;
  logic [4:0] priority_reg$in_;
  logic [4:0] priority_reg$out;
  logic [0:0] priority_reg$reset;

  RegEnRst__Type_Bits5__reset_value_1 priority_reg (
    .clk( priority_reg$clk ),
    .en( priority_reg$en ),
    .in_( priority_reg$in_ ),
    .out( priority_reg$out ),
    .reset( priority_reg$reset )
  );

  // PYMTL SOURCE:
  // 
  // @s.update
  // def comb_grants_int():
  // 
  //   for i in xrange( nreqsX2 ):
  // 
  //     # Set internal grants
  // 
  //     if s.priority_int[i]:
  //       s.grants_int[i] = s.reqs_int[i]
  // 
  //     else:
  //       s.grants_int[i] = ~s.kills[i] & s.reqs_int[i]
  
  always_comb begin : comb_grants_int
    for ( int i = 0; i < _fvar_nreqsX2; i += 1 )
      if ( priority_int[i] ) begin
        grants_int[i] = reqs_int[i];
      end
      else
        grants_int[i] = ( ~kills[i] ) & reqs_int[i];
  end

  // PYMTL SOURCE:
  // 
  // @s.update
  // def comb_priority_en():
  // 
  //   # Set the priority enable
  //   s.priority_en = ( s.grants != Type(0) ) & s.en
  
  always_comb begin : comb_priority_en
    priority_en = ( grants != 5'd0 ) & en;
  end

  // PYMTL SOURCE:
  // 
  // @s.update
  // def comb_priority_int():
  // 
  //   s.priority_int[    0:nreqs  ] = s.priority_reg.out
  //   s.priority_int[nreqs:nreqsX2] = Type(0)
  
  always_comb begin : comb_priority_int
    priority_int[4:0] = priority_reg$out;
    priority_int[9:_fvar_nreqs] = 5'd0;
  end

  // PYMTL SOURCE:
  // 
  // @s.update
  // def comb_kills():
  // 
  //   # Set kill signals
  // 
  //   s.kills[0] = Bits1(1)
  // 
  //   for i in xrange( nreqsX2 ):
  // 
  //     if s.priority_int[i]:
  //       s.kills[i+1] = s.reqs_int[i]
  // 
  //     else:
  //       s.kills[i+1] = s.kills[i] | ( ~s.kills[i] & s.reqs_int[i] )
  
  always_comb begin : comb_kills
    kills[0] = 1'd1;
    for ( int i = 0; i < _fvar_nreqsX2; i += 1 )
      if ( priority_int[i] ) begin
        kills[i + 1] = reqs_int[i];
      end
      else
        kills[i + 1] = kills[i] | ( ( ~kills[i] ) & reqs_int[i] );
  end

  // PYMTL SOURCE:
  // 
  // @s.update
  // def comb_reqs_int():
  // 
  //   s.reqs_int    [    0:nreqs  ] = s.reqs
  //   s.reqs_int    [nreqs:nreqsX2] = s.reqs
  
  always_comb begin : comb_reqs_int
    reqs_int[4:0] = reqs;
    reqs_int[9:_fvar_nreqs] = reqs;
  end

  // PYMTL SOURCE:
  // 
  // @s.update
  // def comb_grants():
  // 
  //   # Assign the output ports
  //   for i in range( nreqs ):
  //     s.grants[i] = s.grants_int[i] | s.grants_int[nreqs+i]
  
  always_comb begin : comb_grants
    for ( int i = 0; i < _fvar_nreqs; i += 1 )
      grants[i] = grants_int[i] | grants_int[_fvar_nreqs + i];
  end

  assign priority_reg$clk = clk;
  assign priority_reg$reset = reset;
  assign priority_reg$en = priority_en;
  assign priority_reg$in_[4:1] = grants[3:0];
  assign priority_reg$in_[0:0] = grants[4:4];

endmodule


module Mux__Type_Packet__ninputs_5
(
  input logic [0:0] clk,
  input Packet in_ [0:4],
  output Packet out,
  input logic [0:0] reset,
  input logic [2:0] sel
);

  // PYMTL SOURCE:
  // 
  // @s.update
  // def up_mux():
  //   s.out = s.in_[ s.sel ]
  
  always_comb begin : up_mux
    out = in_[sel];
  end

endmodule


module SwitchUnitRTL__PacketType_Packet__num_inports_5
(
  input logic [0:0] clk,
  input logic [0:0] reset,
  output logic [0:0] get_$0_$en,
  input Packet get_$0_$msg,
  input logic [0:0] get_$0_$rdy,
  output logic [0:0] get_$1_$en,
  input Packet get_$1_$msg,
  input logic [0:0] get_$1_$rdy,
  output logic [0:0] get_$2_$en,
  input Packet get_$2_$msg,
  input logic [0:0] get_$2_$rdy,
  output logic [0:0] get_$3_$en,
  input Packet get_$3_$msg,
  input logic [0:0] get_$3_$rdy,
  output logic [0:0] get_$4_$en,
  input Packet get_$4_$msg,
  input logic [0:0] get_$4_$rdy,
  output logic [0:0] send_$en,
  output Packet send_$msg,
  input logic [0:0] send_$rdy
);
  localparam [31:0] num_inports = 32'd5;
  localparam [31:0] sel_width = 32'd3;
  logic [0:0] arbiter$clk;
  logic [0:0] arbiter$en;
  logic [4:0] arbiter$grants;
  logic [4:0] arbiter$reqs;
  logic [0:0] arbiter$reset;

  RoundRobinArbiterEn__nreqs_5 arbiter (
    .clk( arbiter$clk ),
    .en( arbiter$en ),
    .grants( arbiter$grants ),
    .reqs( arbiter$reqs ),
    .reset( arbiter$reset )
  );

  logic [0:0] encoder$clk;
  logic [4:0] encoder$in_;
  logic [2:0] encoder$out;
  logic [0:0] encoder$reset;

  Encoder__in_width_5__out_width_3 encoder (
    .clk( encoder$clk ),
    .in_( encoder$in_ ),
    .out( encoder$out ),
    .reset( encoder$reset )
  );

  logic [0:0] mux$clk;
  Packet mux$in_ [0:4];
  Packet mux$out;
  logic [0:0] mux$reset;
  logic [2:0] mux$sel;

  Mux__Type_Packet__ninputs_5 mux (
    .clk( mux$clk ),
    .in_( mux$in_ ),
    .out( mux$out ),
    .reset( mux$reset ),
    .sel( mux$sel )
  );

  // PYMTL SOURCE:
  // 
  // @s.update
  // def up_arb_send_en():
  //   s.arbiter.en = s.arbiter.grants > Bits5(0) and s.send.rdy
  //   s.send.en = s.arbiter.grants > Bits5(0) and s.send.rdy
  
  always_comb begin : up_arb_send_en
    arbiter$en = ( arbiter$grants > 5'd0 ) && send_$rdy;
    send_$en = ( arbiter$grants > 5'd0 ) && send_$rdy;
  end

  // PYMTL SOURCE:
  // 
  // @s.update
  // def up_get_en():
  //   s.get[0].en = (
  //     Bits1(1) if s.get[0].rdy and s.send.rdy and s.mux.sel==Bits3(0) else 
  //     Bits1(0)
  //   ) 
  //   s.get[1].en = (
  //     Bits1(1) if s.get[1].rdy and s.send.rdy and s.mux.sel==Bits3(1) else 
  //     Bits1(0)
  //   ) 
  //   s.get[2].en = (
  //     Bits1(1) if s.get[2].rdy and s.send.rdy and s.mux.sel==Bits3(2) else 
  //     Bits1(0)
  //   ) 
  //   s.get[3].en = (
  //     Bits1(1) if s.get[3].rdy and s.send.rdy and s.mux.sel==Bits3(3) else 
  //     Bits1(0)
  //   ) 
  //   s.get[4].en = (
  //     Bits1(1) if s.get[4].rdy and s.send.rdy and s.mux.sel==Bits3(4) else 
  //     Bits1(0)
  //   ) 
  
  always_comb begin : up_get_en
    get_$0_$en = ( get_$0_$rdy && send_$rdy && ( mux$sel == 3'd0 ) ) ? 1'd1 : 1'd0;
    get_$1_$en = ( get_$1_$rdy && send_$rdy && ( mux$sel == 3'd1 ) ) ? 1'd1 : 1'd0;
    get_$2_$en = ( get_$2_$rdy && send_$rdy && ( mux$sel == 3'd2 ) ) ? 1'd1 : 1'd0;
    get_$3_$en = ( get_$3_$rdy && send_$rdy && ( mux$sel == 3'd3 ) ) ? 1'd1 : 1'd0;
    get_$4_$en = ( get_$4_$rdy && send_$rdy && ( mux$sel == 3'd4 ) ) ? 1'd1 : 1'd0;
  end

  assign arbiter$clk = clk;
  assign arbiter$reset = reset;
  assign mux$clk = clk;
  assign mux$reset = reset;
  assign send_$msg = mux$out;
  assign encoder$clk = clk;
  assign encoder$reset = reset;
  assign encoder$in_ = arbiter$grants;
  assign mux$sel = encoder$out;
  assign arbiter$reqs[0:0] = get_$0_$rdy;
  assign mux$in_[0] = get_$0_$msg;
  assign arbiter$reqs[1:1] = get_$1_$rdy;
  assign mux$in_[1] = get_$1_$msg;
  assign arbiter$reqs[2:2] = get_$2_$rdy;
  assign mux$in_[2] = get_$2_$msg;
  assign arbiter$reqs[3:3] = get_$3_$rdy;
  assign mux$in_[3] = get_$3_$msg;
  assign arbiter$reqs[4:4] = get_$4_$rdy;
  assign mux$in_[4] = get_$4_$msg;

endmodule


module DORYMeshRouteUnitRTL__PacketType_Packet__PositionType_MeshPosition_9x9__num_outports_5
(
  input logic [0:0] clk,
  input MeshPosition_9x9 pos,
  input logic [0:0] reset,
  output logic [0:0] get_$en,
  input Packet get_$msg,
  input logic [0:0] get_$rdy,
  input logic [0:0] give_$0_$en,
  output Packet give_$0_$msg,
  output logic [0:0] give_$0_$rdy,
  input logic [0:0] give_$1_$en,
  output Packet give_$1_$msg,
  output logic [0:0] give_$1_$rdy,
  input logic [0:0] give_$2_$en,
  output Packet give_$2_$msg,
  output logic [0:0] give_$2_$rdy,
  input logic [0:0] give_$3_$en,
  output Packet give_$3_$msg,
  output logic [0:0] give_$3_$rdy,
  input logic [0:0] give_$4_$en,
  output Packet give_$4_$msg,
  output logic [0:0] give_$4_$rdy
);
  localparam [31:0] num_outports = 32'd5;
  localparam [2:0] _fvar_WEST = 3'd2;
  localparam [2:0] _fvar_SELF = 3'd4;
  localparam [2:0] _fvar_EAST = 3'd3;
  localparam [2:0] _fvar_NORTH = 3'd0;
  localparam [2:0] _fvar_SOUTH = 3'd1;
  logic [4:0] give_ens;
  logic [2:0] out_dir;

  // PYMTL SOURCE:
  // 
  // @s.update
  // def up_ru_get_en():
  //   s.get.en = s.give_ens > Bits5(0) 
  
  always_comb begin : up_ru_get_en
    get_$en = give_ens > 5'd0;
  end

  // PYMTL SOURCE:
  // 
  //    @s.update
  //    def up_ru_routing():
  // 
  //      s.out_dir = Bits3(0)
  //      s.give[0].rdy = Bits1(0)
  //      s.give[1].rdy = Bits1(0)
  //      s.give[2].rdy = Bits1(0)
  //      s.give[3].rdy = Bits1(0)
  //      s.give[4].rdy = Bits1(0)
  // 
  //      if s.get.rdy:
  //        if s.pos.pos_x == s.get.msg.dst_x and s.pos.pos_y == s.get.msg.dst_y:
  //          s.out_dir = SELF
  //          s.give[0].rdy = Bits1(1)
  //        elif s.get.msg.dst_y < s.pos.pos_y:
  //          s.out_dir = SOUTH
  //          s.give[2].rdy = Bits1(1)
  //        elif s.get.msg.dst_y > s.pos.pos_y:
  //          s.out_dir = NORTH
  //          s.give[1].rdy = Bits1(1)
  //        elif s.get.msg.dst_x < s.pos.pos_x:
  //          s.out_dir = WEST
  //          s.give[3].rdy = Bits1(1)
  //        else:
  //          s.out_dir = EAST
  //          s.give[4].rdy = Bits1(1)
  
  always_comb begin : up_ru_routing
    out_dir = 3'd0;
    give_$0_$rdy = 1'd0;
    give_$1_$rdy = 1'd0;
    give_$2_$rdy = 1'd0;
    give_$3_$rdy = 1'd0;
    give_$4_$rdy = 1'd0;
    if ( get_$rdy ) begin
      if ( ( pos.pos_x == get_$msg.dst_x ) && ( pos.pos_y == get_$msg.dst_y ) ) begin
        out_dir = _fvar_SELF;
        give_$0_$rdy = 1'd1;
      end
      else if ( get_$msg.dst_y < pos.pos_y ) begin
        out_dir = _fvar_SOUTH;
        give_$2_$rdy = 1'd1;
      end
      else if ( get_$msg.dst_y > pos.pos_y ) begin
        out_dir = _fvar_NORTH;
        give_$1_$rdy = 1'd1;
      end
      else if ( get_$msg.dst_x < pos.pos_x ) begin
        out_dir = _fvar_WEST;
        give_$3_$rdy = 1'd1;
      end
      else begin
        out_dir = _fvar_EAST;
        give_$4_$rdy = 1'd1;
      end
    end
  end

  assign give_$0_$msg = get_$msg;
  assign give_ens[0:0] = give_$0_$en;
  assign give_$1_$msg = get_$msg;
  assign give_ens[1:1] = give_$1_$en;
  assign give_$2_$msg = get_$msg;
  assign give_ens[2:2] = give_$2_$en;
  assign give_$3_$msg = get_$msg;
  assign give_ens[3:3] = give_$3_$en;
  assign give_$4_$msg = get_$msg;
  assign give_ens[4:4] = give_$4_$en;

endmodule


module toprouter
(
  input logic [0:0] clk,
  input MeshPosition_9x9 pos,
  input logic [0:0] reset,
  input logic [0:0] recv_$0_$en,
  input Packet recv_$0_$msg,
  output logic [0:0] recv_$0_$rdy,
  input logic [0:0] recv_$1_$en,
  input Packet recv_$1_$msg,
  output logic [0:0] recv_$1_$rdy,
  input logic [0:0] recv_$2_$en,
  input Packet recv_$2_$msg,
  output logic [0:0] recv_$2_$rdy,
  input logic [0:0] recv_$3_$en,
  input Packet recv_$3_$msg,
  output logic [0:0] recv_$3_$rdy,
  input logic [0:0] recv_$4_$en,
  input Packet recv_$4_$msg,
  output logic [0:0] recv_$4_$rdy,
  output logic [0:0] send_$0_$en,
  output Packet send_$0_$msg,
  input logic [0:0] send_$0_$rdy,
  output logic [0:0] send_$1_$en,
  output Packet send_$1_$msg,
  input logic [0:0] send_$1_$rdy,
  output logic [0:0] send_$2_$en,
  output Packet send_$2_$msg,
  input logic [0:0] send_$2_$rdy,
  output logic [0:0] send_$3_$en,
  output Packet send_$3_$msg,
  input logic [0:0] send_$3_$rdy,
  output logic [0:0] send_$4_$en,
  output Packet send_$4_$msg,
  input logic [0:0] send_$4_$rdy
);
  localparam [31:0] num_inports = 32'd5;
  localparam [31:0] num_outports = 32'd5;
  logic [0:0] input_units_$0$clk;
  logic [0:0] input_units_$0$reset;
  logic [0:0] input_units_$0$give_$en;
  Packet input_units_$0$give_$msg;
  logic [0:0] input_units_$0$give_$rdy;
  logic [0:0] input_units_$0$recv_$en;
  Packet input_units_$0$recv_$msg;
  logic [0:0] input_units_$0$recv_$rdy;

  InputUnitRTL__PacketType_Packet__QueueType_NormalQueueRTL input_units_$0 (
    .clk( input_units_$0$clk ),
    .reset( input_units_$0$reset ),
    .give_$en( input_units_$0$give_$en ),
    .give_$msg( input_units_$0$give_$msg ),
    .give_$rdy( input_units_$0$give_$rdy ),
    .recv_$en( input_units_$0$recv_$en ),
    .recv_$msg( input_units_$0$recv_$msg ),
    .recv_$rdy( input_units_$0$recv_$rdy )
  );

  logic [0:0] input_units_$1$clk;
  logic [0:0] input_units_$1$reset;
  logic [0:0] input_units_$1$give_$en;
  Packet input_units_$1$give_$msg;
  logic [0:0] input_units_$1$give_$rdy;
  logic [0:0] input_units_$1$recv_$en;
  Packet input_units_$1$recv_$msg;
  logic [0:0] input_units_$1$recv_$rdy;

  InputUnitRTL__PacketType_Packet__QueueType_NormalQueueRTL input_units_$1 (
    .clk( input_units_$1$clk ),
    .reset( input_units_$1$reset ),
    .give_$en( input_units_$1$give_$en ),
    .give_$msg( input_units_$1$give_$msg ),
    .give_$rdy( input_units_$1$give_$rdy ),
    .recv_$en( input_units_$1$recv_$en ),
    .recv_$msg( input_units_$1$recv_$msg ),
    .recv_$rdy( input_units_$1$recv_$rdy )
  );

  logic [0:0] input_units_$2$clk;
  logic [0:0] input_units_$2$reset;
  logic [0:0] input_units_$2$give_$en;
  Packet input_units_$2$give_$msg;
  logic [0:0] input_units_$2$give_$rdy;
  logic [0:0] input_units_$2$recv_$en;
  Packet input_units_$2$recv_$msg;
  logic [0:0] input_units_$2$recv_$rdy;

  InputUnitRTL__PacketType_Packet__QueueType_NormalQueueRTL input_units_$2 (
    .clk( input_units_$2$clk ),
    .reset( input_units_$2$reset ),
    .give_$en( input_units_$2$give_$en ),
    .give_$msg( input_units_$2$give_$msg ),
    .give_$rdy( input_units_$2$give_$rdy ),
    .recv_$en( input_units_$2$recv_$en ),
    .recv_$msg( input_units_$2$recv_$msg ),
    .recv_$rdy( input_units_$2$recv_$rdy )
  );

  logic [0:0] input_units_$3$clk;
  logic [0:0] input_units_$3$reset;
  logic [0:0] input_units_$3$give_$en;
  Packet input_units_$3$give_$msg;
  logic [0:0] input_units_$3$give_$rdy;
  logic [0:0] input_units_$3$recv_$en;
  Packet input_units_$3$recv_$msg;
  logic [0:0] input_units_$3$recv_$rdy;

  InputUnitRTL__PacketType_Packet__QueueType_NormalQueueRTL input_units_$3 (
    .clk( input_units_$3$clk ),
    .reset( input_units_$3$reset ),
    .give_$en( input_units_$3$give_$en ),
    .give_$msg( input_units_$3$give_$msg ),
    .give_$rdy( input_units_$3$give_$rdy ),
    .recv_$en( input_units_$3$recv_$en ),
    .recv_$msg( input_units_$3$recv_$msg ),
    .recv_$rdy( input_units_$3$recv_$rdy )
  );

  logic [0:0] input_units_$4$clk;
  logic [0:0] input_units_$4$reset;
  logic [0:0] input_units_$4$give_$en;
  Packet input_units_$4$give_$msg;
  logic [0:0] input_units_$4$give_$rdy;
  logic [0:0] input_units_$4$recv_$en;
  Packet input_units_$4$recv_$msg;
  logic [0:0] input_units_$4$recv_$rdy;

  InputUnitRTL__PacketType_Packet__QueueType_NormalQueueRTL input_units_$4 (
    .clk( input_units_$4$clk ),
    .reset( input_units_$4$reset ),
    .give_$en( input_units_$4$give_$en ),
    .give_$msg( input_units_$4$give_$msg ),
    .give_$rdy( input_units_$4$give_$rdy ),
    .recv_$en( input_units_$4$recv_$en ),
    .recv_$msg( input_units_$4$recv_$msg ),
    .recv_$rdy( input_units_$4$recv_$rdy )
  );

  logic [0:0] output_units_$0$clk;
  logic [0:0] output_units_$0$reset;
  logic [0:0] output_units_$0$recv_$en;
  Packet output_units_$0$recv_$msg;
  logic [0:0] output_units_$0$recv_$rdy;
  logic [0:0] output_units_$0$send_$en;
  Packet output_units_$0$send_$msg;
  logic [0:0] output_units_$0$send_$rdy;

  OutputUnitRTL__PacketType_Packet__QueueType_None output_units_$0 (
    .clk( output_units_$0$clk ),
    .reset( output_units_$0$reset ),
    .recv_$en( output_units_$0$recv_$en ),
    .recv_$msg( output_units_$0$recv_$msg ),
    .recv_$rdy( output_units_$0$recv_$rdy ),
    .send_$en( output_units_$0$send_$en ),
    .send_$msg( output_units_$0$send_$msg ),
    .send_$rdy( output_units_$0$send_$rdy )
  );

  logic [0:0] output_units_$1$clk;
  logic [0:0] output_units_$1$reset;
  logic [0:0] output_units_$1$recv_$en;
  Packet output_units_$1$recv_$msg;
  logic [0:0] output_units_$1$recv_$rdy;
  logic [0:0] output_units_$1$send_$en;
  Packet output_units_$1$send_$msg;
  logic [0:0] output_units_$1$send_$rdy;

  OutputUnitRTL__PacketType_Packet__QueueType_None output_units_$1 (
    .clk( output_units_$1$clk ),
    .reset( output_units_$1$reset ),
    .recv_$en( output_units_$1$recv_$en ),
    .recv_$msg( output_units_$1$recv_$msg ),
    .recv_$rdy( output_units_$1$recv_$rdy ),
    .send_$en( output_units_$1$send_$en ),
    .send_$msg( output_units_$1$send_$msg ),
    .send_$rdy( output_units_$1$send_$rdy )
  );

  logic [0:0] output_units_$2$clk;
  logic [0:0] output_units_$2$reset;
  logic [0:0] output_units_$2$recv_$en;
  Packet output_units_$2$recv_$msg;
  logic [0:0] output_units_$2$recv_$rdy;
  logic [0:0] output_units_$2$send_$en;
  Packet output_units_$2$send_$msg;
  logic [0:0] output_units_$2$send_$rdy;

  OutputUnitRTL__PacketType_Packet__QueueType_None output_units_$2 (
    .clk( output_units_$2$clk ),
    .reset( output_units_$2$reset ),
    .recv_$en( output_units_$2$recv_$en ),
    .recv_$msg( output_units_$2$recv_$msg ),
    .recv_$rdy( output_units_$2$recv_$rdy ),
    .send_$en( output_units_$2$send_$en ),
    .send_$msg( output_units_$2$send_$msg ),
    .send_$rdy( output_units_$2$send_$rdy )
  );

  logic [0:0] output_units_$3$clk;
  logic [0:0] output_units_$3$reset;
  logic [0:0] output_units_$3$recv_$en;
  Packet output_units_$3$recv_$msg;
  logic [0:0] output_units_$3$recv_$rdy;
  logic [0:0] output_units_$3$send_$en;
  Packet output_units_$3$send_$msg;
  logic [0:0] output_units_$3$send_$rdy;

  OutputUnitRTL__PacketType_Packet__QueueType_None output_units_$3 (
    .clk( output_units_$3$clk ),
    .reset( output_units_$3$reset ),
    .recv_$en( output_units_$3$recv_$en ),
    .recv_$msg( output_units_$3$recv_$msg ),
    .recv_$rdy( output_units_$3$recv_$rdy ),
    .send_$en( output_units_$3$send_$en ),
    .send_$msg( output_units_$3$send_$msg ),
    .send_$rdy( output_units_$3$send_$rdy )
  );

  logic [0:0] output_units_$4$clk;
  logic [0:0] output_units_$4$reset;
  logic [0:0] output_units_$4$recv_$en;
  Packet output_units_$4$recv_$msg;
  logic [0:0] output_units_$4$recv_$rdy;
  logic [0:0] output_units_$4$send_$en;
  Packet output_units_$4$send_$msg;
  logic [0:0] output_units_$4$send_$rdy;

  OutputUnitRTL__PacketType_Packet__QueueType_None output_units_$4 (
    .clk( output_units_$4$clk ),
    .reset( output_units_$4$reset ),
    .recv_$en( output_units_$4$recv_$en ),
    .recv_$msg( output_units_$4$recv_$msg ),
    .recv_$rdy( output_units_$4$recv_$rdy ),
    .send_$en( output_units_$4$send_$en ),
    .send_$msg( output_units_$4$send_$msg ),
    .send_$rdy( output_units_$4$send_$rdy )
  );

  logic [0:0] route_units_$0$clk;
  MeshPosition_9x9 route_units_$0$pos;
  logic [0:0] route_units_$0$reset;
  logic [0:0] route_units_$0$get_$en;
  Packet route_units_$0$get_$msg;
  logic [0:0] route_units_$0$get_$rdy;
  logic [0:0] route_units_$0$give_$0_$en;
  Packet route_units_$0$give_$0_$msg;
  logic [0:0] route_units_$0$give_$0_$rdy;
  logic [0:0] route_units_$0$give_$1_$en;
  Packet route_units_$0$give_$1_$msg;
  logic [0:0] route_units_$0$give_$1_$rdy;
  logic [0:0] route_units_$0$give_$2_$en;
  Packet route_units_$0$give_$2_$msg;
  logic [0:0] route_units_$0$give_$2_$rdy;
  logic [0:0] route_units_$0$give_$3_$en;
  Packet route_units_$0$give_$3_$msg;
  logic [0:0] route_units_$0$give_$3_$rdy;
  logic [0:0] route_units_$0$give_$4_$en;
  Packet route_units_$0$give_$4_$msg;
  logic [0:0] route_units_$0$give_$4_$rdy;

  DORYMeshRouteUnitRTL__PacketType_Packet__PositionType_MeshPosition_9x9__num_outports_5 route_units_$0 (
    .clk( route_units_$0$clk ),
    .pos( route_units_$0$pos ),
    .reset( route_units_$0$reset ),
    .get_$en( route_units_$0$get_$en ),
    .get_$msg( route_units_$0$get_$msg ),
    .get_$rdy( route_units_$0$get_$rdy ),
    .give_$0_$en( route_units_$0$give_$0_$en ),
    .give_$0_$msg( route_units_$0$give_$0_$msg ),
    .give_$0_$rdy( route_units_$0$give_$0_$rdy ),
    .give_$1_$en( route_units_$0$give_$1_$en ),
    .give_$1_$msg( route_units_$0$give_$1_$msg ),
    .give_$1_$rdy( route_units_$0$give_$1_$rdy ),
    .give_$2_$en( route_units_$0$give_$2_$en ),
    .give_$2_$msg( route_units_$0$give_$2_$msg ),
    .give_$2_$rdy( route_units_$0$give_$2_$rdy ),
    .give_$3_$en( route_units_$0$give_$3_$en ),
    .give_$3_$msg( route_units_$0$give_$3_$msg ),
    .give_$3_$rdy( route_units_$0$give_$3_$rdy ),
    .give_$4_$en( route_units_$0$give_$4_$en ),
    .give_$4_$msg( route_units_$0$give_$4_$msg ),
    .give_$4_$rdy( route_units_$0$give_$4_$rdy )
  );

  logic [0:0] route_units_$1$clk;
  MeshPosition_9x9 route_units_$1$pos;
  logic [0:0] route_units_$1$reset;
  logic [0:0] route_units_$1$get_$en;
  Packet route_units_$1$get_$msg;
  logic [0:0] route_units_$1$get_$rdy;
  logic [0:0] route_units_$1$give_$0_$en;
  Packet route_units_$1$give_$0_$msg;
  logic [0:0] route_units_$1$give_$0_$rdy;
  logic [0:0] route_units_$1$give_$1_$en;
  Packet route_units_$1$give_$1_$msg;
  logic [0:0] route_units_$1$give_$1_$rdy;
  logic [0:0] route_units_$1$give_$2_$en;
  Packet route_units_$1$give_$2_$msg;
  logic [0:0] route_units_$1$give_$2_$rdy;
  logic [0:0] route_units_$1$give_$3_$en;
  Packet route_units_$1$give_$3_$msg;
  logic [0:0] route_units_$1$give_$3_$rdy;
  logic [0:0] route_units_$1$give_$4_$en;
  Packet route_units_$1$give_$4_$msg;
  logic [0:0] route_units_$1$give_$4_$rdy;

  DORYMeshRouteUnitRTL__PacketType_Packet__PositionType_MeshPosition_9x9__num_outports_5 route_units_$1 (
    .clk( route_units_$1$clk ),
    .pos( route_units_$1$pos ),
    .reset( route_units_$1$reset ),
    .get_$en( route_units_$1$get_$en ),
    .get_$msg( route_units_$1$get_$msg ),
    .get_$rdy( route_units_$1$get_$rdy ),
    .give_$0_$en( route_units_$1$give_$0_$en ),
    .give_$0_$msg( route_units_$1$give_$0_$msg ),
    .give_$0_$rdy( route_units_$1$give_$0_$rdy ),
    .give_$1_$en( route_units_$1$give_$1_$en ),
    .give_$1_$msg( route_units_$1$give_$1_$msg ),
    .give_$1_$rdy( route_units_$1$give_$1_$rdy ),
    .give_$2_$en( route_units_$1$give_$2_$en ),
    .give_$2_$msg( route_units_$1$give_$2_$msg ),
    .give_$2_$rdy( route_units_$1$give_$2_$rdy ),
    .give_$3_$en( route_units_$1$give_$3_$en ),
    .give_$3_$msg( route_units_$1$give_$3_$msg ),
    .give_$3_$rdy( route_units_$1$give_$3_$rdy ),
    .give_$4_$en( route_units_$1$give_$4_$en ),
    .give_$4_$msg( route_units_$1$give_$4_$msg ),
    .give_$4_$rdy( route_units_$1$give_$4_$rdy )
  );

  logic [0:0] route_units_$2$clk;
  MeshPosition_9x9 route_units_$2$pos;
  logic [0:0] route_units_$2$reset;
  logic [0:0] route_units_$2$get_$en;
  Packet route_units_$2$get_$msg;
  logic [0:0] route_units_$2$get_$rdy;
  logic [0:0] route_units_$2$give_$0_$en;
  Packet route_units_$2$give_$0_$msg;
  logic [0:0] route_units_$2$give_$0_$rdy;
  logic [0:0] route_units_$2$give_$1_$en;
  Packet route_units_$2$give_$1_$msg;
  logic [0:0] route_units_$2$give_$1_$rdy;
  logic [0:0] route_units_$2$give_$2_$en;
  Packet route_units_$2$give_$2_$msg;
  logic [0:0] route_units_$2$give_$2_$rdy;
  logic [0:0] route_units_$2$give_$3_$en;
  Packet route_units_$2$give_$3_$msg;
  logic [0:0] route_units_$2$give_$3_$rdy;
  logic [0:0] route_units_$2$give_$4_$en;
  Packet route_units_$2$give_$4_$msg;
  logic [0:0] route_units_$2$give_$4_$rdy;

  DORYMeshRouteUnitRTL__PacketType_Packet__PositionType_MeshPosition_9x9__num_outports_5 route_units_$2 (
    .clk( route_units_$2$clk ),
    .pos( route_units_$2$pos ),
    .reset( route_units_$2$reset ),
    .get_$en( route_units_$2$get_$en ),
    .get_$msg( route_units_$2$get_$msg ),
    .get_$rdy( route_units_$2$get_$rdy ),
    .give_$0_$en( route_units_$2$give_$0_$en ),
    .give_$0_$msg( route_units_$2$give_$0_$msg ),
    .give_$0_$rdy( route_units_$2$give_$0_$rdy ),
    .give_$1_$en( route_units_$2$give_$1_$en ),
    .give_$1_$msg( route_units_$2$give_$1_$msg ),
    .give_$1_$rdy( route_units_$2$give_$1_$rdy ),
    .give_$2_$en( route_units_$2$give_$2_$en ),
    .give_$2_$msg( route_units_$2$give_$2_$msg ),
    .give_$2_$rdy( route_units_$2$give_$2_$rdy ),
    .give_$3_$en( route_units_$2$give_$3_$en ),
    .give_$3_$msg( route_units_$2$give_$3_$msg ),
    .give_$3_$rdy( route_units_$2$give_$3_$rdy ),
    .give_$4_$en( route_units_$2$give_$4_$en ),
    .give_$4_$msg( route_units_$2$give_$4_$msg ),
    .give_$4_$rdy( route_units_$2$give_$4_$rdy )
  );

  logic [0:0] route_units_$3$clk;
  MeshPosition_9x9 route_units_$3$pos;
  logic [0:0] route_units_$3$reset;
  logic [0:0] route_units_$3$get_$en;
  Packet route_units_$3$get_$msg;
  logic [0:0] route_units_$3$get_$rdy;
  logic [0:0] route_units_$3$give_$0_$en;
  Packet route_units_$3$give_$0_$msg;
  logic [0:0] route_units_$3$give_$0_$rdy;
  logic [0:0] route_units_$3$give_$1_$en;
  Packet route_units_$3$give_$1_$msg;
  logic [0:0] route_units_$3$give_$1_$rdy;
  logic [0:0] route_units_$3$give_$2_$en;
  Packet route_units_$3$give_$2_$msg;
  logic [0:0] route_units_$3$give_$2_$rdy;
  logic [0:0] route_units_$3$give_$3_$en;
  Packet route_units_$3$give_$3_$msg;
  logic [0:0] route_units_$3$give_$3_$rdy;
  logic [0:0] route_units_$3$give_$4_$en;
  Packet route_units_$3$give_$4_$msg;
  logic [0:0] route_units_$3$give_$4_$rdy;

  DORYMeshRouteUnitRTL__PacketType_Packet__PositionType_MeshPosition_9x9__num_outports_5 route_units_$3 (
    .clk( route_units_$3$clk ),
    .pos( route_units_$3$pos ),
    .reset( route_units_$3$reset ),
    .get_$en( route_units_$3$get_$en ),
    .get_$msg( route_units_$3$get_$msg ),
    .get_$rdy( route_units_$3$get_$rdy ),
    .give_$0_$en( route_units_$3$give_$0_$en ),
    .give_$0_$msg( route_units_$3$give_$0_$msg ),
    .give_$0_$rdy( route_units_$3$give_$0_$rdy ),
    .give_$1_$en( route_units_$3$give_$1_$en ),
    .give_$1_$msg( route_units_$3$give_$1_$msg ),
    .give_$1_$rdy( route_units_$3$give_$1_$rdy ),
    .give_$2_$en( route_units_$3$give_$2_$en ),
    .give_$2_$msg( route_units_$3$give_$2_$msg ),
    .give_$2_$rdy( route_units_$3$give_$2_$rdy ),
    .give_$3_$en( route_units_$3$give_$3_$en ),
    .give_$3_$msg( route_units_$3$give_$3_$msg ),
    .give_$3_$rdy( route_units_$3$give_$3_$rdy ),
    .give_$4_$en( route_units_$3$give_$4_$en ),
    .give_$4_$msg( route_units_$3$give_$4_$msg ),
    .give_$4_$rdy( route_units_$3$give_$4_$rdy )
  );

  logic [0:0] route_units_$4$clk;
  MeshPosition_9x9 route_units_$4$pos;
  logic [0:0] route_units_$4$reset;
  logic [0:0] route_units_$4$get_$en;
  Packet route_units_$4$get_$msg;
  logic [0:0] route_units_$4$get_$rdy;
  logic [0:0] route_units_$4$give_$0_$en;
  Packet route_units_$4$give_$0_$msg;
  logic [0:0] route_units_$4$give_$0_$rdy;
  logic [0:0] route_units_$4$give_$1_$en;
  Packet route_units_$4$give_$1_$msg;
  logic [0:0] route_units_$4$give_$1_$rdy;
  logic [0:0] route_units_$4$give_$2_$en;
  Packet route_units_$4$give_$2_$msg;
  logic [0:0] route_units_$4$give_$2_$rdy;
  logic [0:0] route_units_$4$give_$3_$en;
  Packet route_units_$4$give_$3_$msg;
  logic [0:0] route_units_$4$give_$3_$rdy;
  logic [0:0] route_units_$4$give_$4_$en;
  Packet route_units_$4$give_$4_$msg;
  logic [0:0] route_units_$4$give_$4_$rdy;

  DORYMeshRouteUnitRTL__PacketType_Packet__PositionType_MeshPosition_9x9__num_outports_5 route_units_$4 (
    .clk( route_units_$4$clk ),
    .pos( route_units_$4$pos ),
    .reset( route_units_$4$reset ),
    .get_$en( route_units_$4$get_$en ),
    .get_$msg( route_units_$4$get_$msg ),
    .get_$rdy( route_units_$4$get_$rdy ),
    .give_$0_$en( route_units_$4$give_$0_$en ),
    .give_$0_$msg( route_units_$4$give_$0_$msg ),
    .give_$0_$rdy( route_units_$4$give_$0_$rdy ),
    .give_$1_$en( route_units_$4$give_$1_$en ),
    .give_$1_$msg( route_units_$4$give_$1_$msg ),
    .give_$1_$rdy( route_units_$4$give_$1_$rdy ),
    .give_$2_$en( route_units_$4$give_$2_$en ),
    .give_$2_$msg( route_units_$4$give_$2_$msg ),
    .give_$2_$rdy( route_units_$4$give_$2_$rdy ),
    .give_$3_$en( route_units_$4$give_$3_$en ),
    .give_$3_$msg( route_units_$4$give_$3_$msg ),
    .give_$3_$rdy( route_units_$4$give_$3_$rdy ),
    .give_$4_$en( route_units_$4$give_$4_$en ),
    .give_$4_$msg( route_units_$4$give_$4_$msg ),
    .give_$4_$rdy( route_units_$4$give_$4_$rdy )
  );

  logic [0:0] switch_units_$0$clk;
  logic [0:0] switch_units_$0$reset;
  logic [0:0] switch_units_$0$get_$0_$en;
  Packet switch_units_$0$get_$0_$msg;
  logic [0:0] switch_units_$0$get_$0_$rdy;
  logic [0:0] switch_units_$0$get_$1_$en;
  Packet switch_units_$0$get_$1_$msg;
  logic [0:0] switch_units_$0$get_$1_$rdy;
  logic [0:0] switch_units_$0$get_$2_$en;
  Packet switch_units_$0$get_$2_$msg;
  logic [0:0] switch_units_$0$get_$2_$rdy;
  logic [0:0] switch_units_$0$get_$3_$en;
  Packet switch_units_$0$get_$3_$msg;
  logic [0:0] switch_units_$0$get_$3_$rdy;
  logic [0:0] switch_units_$0$get_$4_$en;
  Packet switch_units_$0$get_$4_$msg;
  logic [0:0] switch_units_$0$get_$4_$rdy;
  logic [0:0] switch_units_$0$send_$en;
  Packet switch_units_$0$send_$msg;
  logic [0:0] switch_units_$0$send_$rdy;

  SwitchUnitRTL__PacketType_Packet__num_inports_5 switch_units_$0 (
    .clk( switch_units_$0$clk ),
    .reset( switch_units_$0$reset ),
    .get_$0_$en( switch_units_$0$get_$0_$en ),
    .get_$0_$msg( switch_units_$0$get_$0_$msg ),
    .get_$0_$rdy( switch_units_$0$get_$0_$rdy ),
    .get_$1_$en( switch_units_$0$get_$1_$en ),
    .get_$1_$msg( switch_units_$0$get_$1_$msg ),
    .get_$1_$rdy( switch_units_$0$get_$1_$rdy ),
    .get_$2_$en( switch_units_$0$get_$2_$en ),
    .get_$2_$msg( switch_units_$0$get_$2_$msg ),
    .get_$2_$rdy( switch_units_$0$get_$2_$rdy ),
    .get_$3_$en( switch_units_$0$get_$3_$en ),
    .get_$3_$msg( switch_units_$0$get_$3_$msg ),
    .get_$3_$rdy( switch_units_$0$get_$3_$rdy ),
    .get_$4_$en( switch_units_$0$get_$4_$en ),
    .get_$4_$msg( switch_units_$0$get_$4_$msg ),
    .get_$4_$rdy( switch_units_$0$get_$4_$rdy ),
    .send_$en( switch_units_$0$send_$en ),
    .send_$msg( switch_units_$0$send_$msg ),
    .send_$rdy( switch_units_$0$send_$rdy )
  );

  logic [0:0] switch_units_$1$clk;
  logic [0:0] switch_units_$1$reset;
  logic [0:0] switch_units_$1$get_$0_$en;
  Packet switch_units_$1$get_$0_$msg;
  logic [0:0] switch_units_$1$get_$0_$rdy;
  logic [0:0] switch_units_$1$get_$1_$en;
  Packet switch_units_$1$get_$1_$msg;
  logic [0:0] switch_units_$1$get_$1_$rdy;
  logic [0:0] switch_units_$1$get_$2_$en;
  Packet switch_units_$1$get_$2_$msg;
  logic [0:0] switch_units_$1$get_$2_$rdy;
  logic [0:0] switch_units_$1$get_$3_$en;
  Packet switch_units_$1$get_$3_$msg;
  logic [0:0] switch_units_$1$get_$3_$rdy;
  logic [0:0] switch_units_$1$get_$4_$en;
  Packet switch_units_$1$get_$4_$msg;
  logic [0:0] switch_units_$1$get_$4_$rdy;
  logic [0:0] switch_units_$1$send_$en;
  Packet switch_units_$1$send_$msg;
  logic [0:0] switch_units_$1$send_$rdy;

  SwitchUnitRTL__PacketType_Packet__num_inports_5 switch_units_$1 (
    .clk( switch_units_$1$clk ),
    .reset( switch_units_$1$reset ),
    .get_$0_$en( switch_units_$1$get_$0_$en ),
    .get_$0_$msg( switch_units_$1$get_$0_$msg ),
    .get_$0_$rdy( switch_units_$1$get_$0_$rdy ),
    .get_$1_$en( switch_units_$1$get_$1_$en ),
    .get_$1_$msg( switch_units_$1$get_$1_$msg ),
    .get_$1_$rdy( switch_units_$1$get_$1_$rdy ),
    .get_$2_$en( switch_units_$1$get_$2_$en ),
    .get_$2_$msg( switch_units_$1$get_$2_$msg ),
    .get_$2_$rdy( switch_units_$1$get_$2_$rdy ),
    .get_$3_$en( switch_units_$1$get_$3_$en ),
    .get_$3_$msg( switch_units_$1$get_$3_$msg ),
    .get_$3_$rdy( switch_units_$1$get_$3_$rdy ),
    .get_$4_$en( switch_units_$1$get_$4_$en ),
    .get_$4_$msg( switch_units_$1$get_$4_$msg ),
    .get_$4_$rdy( switch_units_$1$get_$4_$rdy ),
    .send_$en( switch_units_$1$send_$en ),
    .send_$msg( switch_units_$1$send_$msg ),
    .send_$rdy( switch_units_$1$send_$rdy )
  );

  logic [0:0] switch_units_$2$clk;
  logic [0:0] switch_units_$2$reset;
  logic [0:0] switch_units_$2$get_$0_$en;
  Packet switch_units_$2$get_$0_$msg;
  logic [0:0] switch_units_$2$get_$0_$rdy;
  logic [0:0] switch_units_$2$get_$1_$en;
  Packet switch_units_$2$get_$1_$msg;
  logic [0:0] switch_units_$2$get_$1_$rdy;
  logic [0:0] switch_units_$2$get_$2_$en;
  Packet switch_units_$2$get_$2_$msg;
  logic [0:0] switch_units_$2$get_$2_$rdy;
  logic [0:0] switch_units_$2$get_$3_$en;
  Packet switch_units_$2$get_$3_$msg;
  logic [0:0] switch_units_$2$get_$3_$rdy;
  logic [0:0] switch_units_$2$get_$4_$en;
  Packet switch_units_$2$get_$4_$msg;
  logic [0:0] switch_units_$2$get_$4_$rdy;
  logic [0:0] switch_units_$2$send_$en;
  Packet switch_units_$2$send_$msg;
  logic [0:0] switch_units_$2$send_$rdy;

  SwitchUnitRTL__PacketType_Packet__num_inports_5 switch_units_$2 (
    .clk( switch_units_$2$clk ),
    .reset( switch_units_$2$reset ),
    .get_$0_$en( switch_units_$2$get_$0_$en ),
    .get_$0_$msg( switch_units_$2$get_$0_$msg ),
    .get_$0_$rdy( switch_units_$2$get_$0_$rdy ),
    .get_$1_$en( switch_units_$2$get_$1_$en ),
    .get_$1_$msg( switch_units_$2$get_$1_$msg ),
    .get_$1_$rdy( switch_units_$2$get_$1_$rdy ),
    .get_$2_$en( switch_units_$2$get_$2_$en ),
    .get_$2_$msg( switch_units_$2$get_$2_$msg ),
    .get_$2_$rdy( switch_units_$2$get_$2_$rdy ),
    .get_$3_$en( switch_units_$2$get_$3_$en ),
    .get_$3_$msg( switch_units_$2$get_$3_$msg ),
    .get_$3_$rdy( switch_units_$2$get_$3_$rdy ),
    .get_$4_$en( switch_units_$2$get_$4_$en ),
    .get_$4_$msg( switch_units_$2$get_$4_$msg ),
    .get_$4_$rdy( switch_units_$2$get_$4_$rdy ),
    .send_$en( switch_units_$2$send_$en ),
    .send_$msg( switch_units_$2$send_$msg ),
    .send_$rdy( switch_units_$2$send_$rdy )
  );

  logic [0:0] switch_units_$3$clk;
  logic [0:0] switch_units_$3$reset;
  logic [0:0] switch_units_$3$get_$0_$en;
  Packet switch_units_$3$get_$0_$msg;
  logic [0:0] switch_units_$3$get_$0_$rdy;
  logic [0:0] switch_units_$3$get_$1_$en;
  Packet switch_units_$3$get_$1_$msg;
  logic [0:0] switch_units_$3$get_$1_$rdy;
  logic [0:0] switch_units_$3$get_$2_$en;
  Packet switch_units_$3$get_$2_$msg;
  logic [0:0] switch_units_$3$get_$2_$rdy;
  logic [0:0] switch_units_$3$get_$3_$en;
  Packet switch_units_$3$get_$3_$msg;
  logic [0:0] switch_units_$3$get_$3_$rdy;
  logic [0:0] switch_units_$3$get_$4_$en;
  Packet switch_units_$3$get_$4_$msg;
  logic [0:0] switch_units_$3$get_$4_$rdy;
  logic [0:0] switch_units_$3$send_$en;
  Packet switch_units_$3$send_$msg;
  logic [0:0] switch_units_$3$send_$rdy;

  SwitchUnitRTL__PacketType_Packet__num_inports_5 switch_units_$3 (
    .clk( switch_units_$3$clk ),
    .reset( switch_units_$3$reset ),
    .get_$0_$en( switch_units_$3$get_$0_$en ),
    .get_$0_$msg( switch_units_$3$get_$0_$msg ),
    .get_$0_$rdy( switch_units_$3$get_$0_$rdy ),
    .get_$1_$en( switch_units_$3$get_$1_$en ),
    .get_$1_$msg( switch_units_$3$get_$1_$msg ),
    .get_$1_$rdy( switch_units_$3$get_$1_$rdy ),
    .get_$2_$en( switch_units_$3$get_$2_$en ),
    .get_$2_$msg( switch_units_$3$get_$2_$msg ),
    .get_$2_$rdy( switch_units_$3$get_$2_$rdy ),
    .get_$3_$en( switch_units_$3$get_$3_$en ),
    .get_$3_$msg( switch_units_$3$get_$3_$msg ),
    .get_$3_$rdy( switch_units_$3$get_$3_$rdy ),
    .get_$4_$en( switch_units_$3$get_$4_$en ),
    .get_$4_$msg( switch_units_$3$get_$4_$msg ),
    .get_$4_$rdy( switch_units_$3$get_$4_$rdy ),
    .send_$en( switch_units_$3$send_$en ),
    .send_$msg( switch_units_$3$send_$msg ),
    .send_$rdy( switch_units_$3$send_$rdy )
  );

  logic [0:0] switch_units_$4$clk;
  logic [0:0] switch_units_$4$reset;
  logic [0:0] switch_units_$4$get_$0_$en;
  Packet switch_units_$4$get_$0_$msg;
  logic [0:0] switch_units_$4$get_$0_$rdy;
  logic [0:0] switch_units_$4$get_$1_$en;
  Packet switch_units_$4$get_$1_$msg;
  logic [0:0] switch_units_$4$get_$1_$rdy;
  logic [0:0] switch_units_$4$get_$2_$en;
  Packet switch_units_$4$get_$2_$msg;
  logic [0:0] switch_units_$4$get_$2_$rdy;
  logic [0:0] switch_units_$4$get_$3_$en;
  Packet switch_units_$4$get_$3_$msg;
  logic [0:0] switch_units_$4$get_$3_$rdy;
  logic [0:0] switch_units_$4$get_$4_$en;
  Packet switch_units_$4$get_$4_$msg;
  logic [0:0] switch_units_$4$get_$4_$rdy;
  logic [0:0] switch_units_$4$send_$en;
  Packet switch_units_$4$send_$msg;
  logic [0:0] switch_units_$4$send_$rdy;

  SwitchUnitRTL__PacketType_Packet__num_inports_5 switch_units_$4 (
    .clk( switch_units_$4$clk ),
    .reset( switch_units_$4$reset ),
    .get_$0_$en( switch_units_$4$get_$0_$en ),
    .get_$0_$msg( switch_units_$4$get_$0_$msg ),
    .get_$0_$rdy( switch_units_$4$get_$0_$rdy ),
    .get_$1_$en( switch_units_$4$get_$1_$en ),
    .get_$1_$msg( switch_units_$4$get_$1_$msg ),
    .get_$1_$rdy( switch_units_$4$get_$1_$rdy ),
    .get_$2_$en( switch_units_$4$get_$2_$en ),
    .get_$2_$msg( switch_units_$4$get_$2_$msg ),
    .get_$2_$rdy( switch_units_$4$get_$2_$rdy ),
    .get_$3_$en( switch_units_$4$get_$3_$en ),
    .get_$3_$msg( switch_units_$4$get_$3_$msg ),
    .get_$3_$rdy( switch_units_$4$get_$3_$rdy ),
    .get_$4_$en( switch_units_$4$get_$4_$en ),
    .get_$4_$msg( switch_units_$4$get_$4_$msg ),
    .get_$4_$rdy( switch_units_$4$get_$4_$rdy ),
    .send_$en( switch_units_$4$send_$en ),
    .send_$msg( switch_units_$4$send_$msg ),
    .send_$rdy( switch_units_$4$send_$rdy )
  );

  assign input_units_$4$clk = clk;
  assign input_units_$4$reset = reset;
  assign input_units_$3$clk = clk;
  assign input_units_$3$reset = reset;
  assign input_units_$2$clk = clk;
  assign input_units_$2$reset = reset;
  assign input_units_$1$clk = clk;
  assign input_units_$1$reset = reset;
  assign input_units_$0$clk = clk;
  assign input_units_$0$reset = reset;
  assign route_units_$4$clk = clk;
  assign route_units_$4$reset = reset;
  assign route_units_$3$clk = clk;
  assign route_units_$3$reset = reset;
  assign route_units_$2$clk = clk;
  assign route_units_$2$reset = reset;
  assign route_units_$1$clk = clk;
  assign route_units_$1$reset = reset;
  assign route_units_$0$clk = clk;
  assign route_units_$0$reset = reset;
  assign switch_units_$4$clk = clk;
  assign switch_units_$4$reset = reset;
  assign switch_units_$3$clk = clk;
  assign switch_units_$3$reset = reset;
  assign switch_units_$2$clk = clk;
  assign switch_units_$2$reset = reset;
  assign switch_units_$1$clk = clk;
  assign switch_units_$1$reset = reset;
  assign switch_units_$0$clk = clk;
  assign switch_units_$0$reset = reset;
  assign output_units_$4$clk = clk;
  assign output_units_$4$reset = reset;
  assign output_units_$3$clk = clk;
  assign output_units_$3$reset = reset;
  assign output_units_$2$clk = clk;
  assign output_units_$2$reset = reset;
  assign output_units_$1$clk = clk;
  assign output_units_$1$reset = reset;
  assign output_units_$0$clk = clk;
  assign output_units_$0$reset = reset;
  assign input_units_$0$recv_$en = recv_$0_$en;
  assign input_units_$0$recv_$msg = recv_$0_$msg;
  assign recv_$0_$rdy = input_units_$0$recv_$rdy;
  assign input_units_$0$give_$en = route_units_$0$get_$en;
  assign route_units_$0$get_$msg = input_units_$0$give_$msg;
  assign route_units_$0$get_$rdy = input_units_$0$give_$rdy;
  assign route_units_$0$pos = pos;
  assign input_units_$1$recv_$en = recv_$1_$en;
  assign input_units_$1$recv_$msg = recv_$1_$msg;
  assign recv_$1_$rdy = input_units_$1$recv_$rdy;
  assign input_units_$1$give_$en = route_units_$1$get_$en;
  assign route_units_$1$get_$msg = input_units_$1$give_$msg;
  assign route_units_$1$get_$rdy = input_units_$1$give_$rdy;
  assign route_units_$1$pos = pos;
  assign input_units_$2$recv_$en = recv_$2_$en;
  assign input_units_$2$recv_$msg = recv_$2_$msg;
  assign recv_$2_$rdy = input_units_$2$recv_$rdy;
  assign input_units_$2$give_$en = route_units_$2$get_$en;
  assign route_units_$2$get_$msg = input_units_$2$give_$msg;
  assign route_units_$2$get_$rdy = input_units_$2$give_$rdy;
  assign route_units_$2$pos = pos;
  assign input_units_$3$recv_$en = recv_$3_$en;
  assign input_units_$3$recv_$msg = recv_$3_$msg;
  assign recv_$3_$rdy = input_units_$3$recv_$rdy;
  assign input_units_$3$give_$en = route_units_$3$get_$en;
  assign route_units_$3$get_$msg = input_units_$3$give_$msg;
  assign route_units_$3$get_$rdy = input_units_$3$give_$rdy;
  assign route_units_$3$pos = pos;
  assign input_units_$4$recv_$en = recv_$4_$en;
  assign input_units_$4$recv_$msg = recv_$4_$msg;
  assign recv_$4_$rdy = input_units_$4$recv_$rdy;
  assign input_units_$4$give_$en = route_units_$4$get_$en;
  assign route_units_$4$get_$msg = input_units_$4$give_$msg;
  assign route_units_$4$get_$rdy = input_units_$4$give_$rdy;
  assign route_units_$4$pos = pos;
  assign route_units_$0$give_$0_$en = switch_units_$0$get_$0_$en;
  assign switch_units_$0$get_$0_$msg = route_units_$0$give_$0_$msg;
  assign switch_units_$0$get_$0_$rdy = route_units_$0$give_$0_$rdy;
  assign route_units_$0$give_$1_$en = switch_units_$1$get_$0_$en;
  assign switch_units_$1$get_$0_$msg = route_units_$0$give_$1_$msg;
  assign switch_units_$1$get_$0_$rdy = route_units_$0$give_$1_$rdy;
  assign route_units_$0$give_$2_$en = switch_units_$2$get_$0_$en;
  assign switch_units_$2$get_$0_$msg = route_units_$0$give_$2_$msg;
  assign switch_units_$2$get_$0_$rdy = route_units_$0$give_$2_$rdy;
  assign route_units_$0$give_$3_$en = switch_units_$3$get_$0_$en;
  assign switch_units_$3$get_$0_$msg = route_units_$0$give_$3_$msg;
  assign switch_units_$3$get_$0_$rdy = route_units_$0$give_$3_$rdy;
  assign route_units_$0$give_$4_$en = switch_units_$4$get_$0_$en;
  assign switch_units_$4$get_$0_$msg = route_units_$0$give_$4_$msg;
  assign switch_units_$4$get_$0_$rdy = route_units_$0$give_$4_$rdy;
  assign route_units_$1$give_$0_$en = switch_units_$0$get_$1_$en;
  assign switch_units_$0$get_$1_$msg = route_units_$1$give_$0_$msg;
  assign switch_units_$0$get_$1_$rdy = route_units_$1$give_$0_$rdy;
  assign route_units_$1$give_$1_$en = switch_units_$1$get_$1_$en;
  assign switch_units_$1$get_$1_$msg = route_units_$1$give_$1_$msg;
  assign switch_units_$1$get_$1_$rdy = route_units_$1$give_$1_$rdy;
  assign route_units_$1$give_$2_$en = switch_units_$2$get_$1_$en;
  assign switch_units_$2$get_$1_$msg = route_units_$1$give_$2_$msg;
  assign switch_units_$2$get_$1_$rdy = route_units_$1$give_$2_$rdy;
  assign route_units_$1$give_$3_$en = switch_units_$3$get_$1_$en;
  assign switch_units_$3$get_$1_$msg = route_units_$1$give_$3_$msg;
  assign switch_units_$3$get_$1_$rdy = route_units_$1$give_$3_$rdy;
  assign route_units_$1$give_$4_$en = switch_units_$4$get_$1_$en;
  assign switch_units_$4$get_$1_$msg = route_units_$1$give_$4_$msg;
  assign switch_units_$4$get_$1_$rdy = route_units_$1$give_$4_$rdy;
  assign route_units_$2$give_$0_$en = switch_units_$0$get_$2_$en;
  assign switch_units_$0$get_$2_$msg = route_units_$2$give_$0_$msg;
  assign switch_units_$0$get_$2_$rdy = route_units_$2$give_$0_$rdy;
  assign route_units_$2$give_$1_$en = switch_units_$1$get_$2_$en;
  assign switch_units_$1$get_$2_$msg = route_units_$2$give_$1_$msg;
  assign switch_units_$1$get_$2_$rdy = route_units_$2$give_$1_$rdy;
  assign route_units_$2$give_$2_$en = switch_units_$2$get_$2_$en;
  assign switch_units_$2$get_$2_$msg = route_units_$2$give_$2_$msg;
  assign switch_units_$2$get_$2_$rdy = route_units_$2$give_$2_$rdy;
  assign route_units_$2$give_$3_$en = switch_units_$3$get_$2_$en;
  assign switch_units_$3$get_$2_$msg = route_units_$2$give_$3_$msg;
  assign switch_units_$3$get_$2_$rdy = route_units_$2$give_$3_$rdy;
  assign route_units_$2$give_$4_$en = switch_units_$4$get_$2_$en;
  assign switch_units_$4$get_$2_$msg = route_units_$2$give_$4_$msg;
  assign switch_units_$4$get_$2_$rdy = route_units_$2$give_$4_$rdy;
  assign route_units_$3$give_$0_$en = switch_units_$0$get_$3_$en;
  assign switch_units_$0$get_$3_$msg = route_units_$3$give_$0_$msg;
  assign switch_units_$0$get_$3_$rdy = route_units_$3$give_$0_$rdy;
  assign route_units_$3$give_$1_$en = switch_units_$1$get_$3_$en;
  assign switch_units_$1$get_$3_$msg = route_units_$3$give_$1_$msg;
  assign switch_units_$1$get_$3_$rdy = route_units_$3$give_$1_$rdy;
  assign route_units_$3$give_$2_$en = switch_units_$2$get_$3_$en;
  assign switch_units_$2$get_$3_$msg = route_units_$3$give_$2_$msg;
  assign switch_units_$2$get_$3_$rdy = route_units_$3$give_$2_$rdy;
  assign route_units_$3$give_$3_$en = switch_units_$3$get_$3_$en;
  assign switch_units_$3$get_$3_$msg = route_units_$3$give_$3_$msg;
  assign switch_units_$3$get_$3_$rdy = route_units_$3$give_$3_$rdy;
  assign route_units_$3$give_$4_$en = switch_units_$4$get_$3_$en;
  assign switch_units_$4$get_$3_$msg = route_units_$3$give_$4_$msg;
  assign switch_units_$4$get_$3_$rdy = route_units_$3$give_$4_$rdy;
  assign route_units_$4$give_$0_$en = switch_units_$0$get_$4_$en;
  assign switch_units_$0$get_$4_$msg = route_units_$4$give_$0_$msg;
  assign switch_units_$0$get_$4_$rdy = route_units_$4$give_$0_$rdy;
  assign route_units_$4$give_$1_$en = switch_units_$1$get_$4_$en;
  assign switch_units_$1$get_$4_$msg = route_units_$4$give_$1_$msg;
  assign switch_units_$1$get_$4_$rdy = route_units_$4$give_$1_$rdy;
  assign route_units_$4$give_$2_$en = switch_units_$2$get_$4_$en;
  assign switch_units_$2$get_$4_$msg = route_units_$4$give_$2_$msg;
  assign switch_units_$2$get_$4_$rdy = route_units_$4$give_$2_$rdy;
  assign route_units_$4$give_$3_$en = switch_units_$3$get_$4_$en;
  assign switch_units_$3$get_$4_$msg = route_units_$4$give_$3_$msg;
  assign switch_units_$3$get_$4_$rdy = route_units_$4$give_$3_$rdy;
  assign route_units_$4$give_$4_$en = switch_units_$4$get_$4_$en;
  assign switch_units_$4$get_$4_$msg = route_units_$4$give_$4_$msg;
  assign switch_units_$4$get_$4_$rdy = route_units_$4$give_$4_$rdy;
  assign output_units_$0$recv_$en = switch_units_$0$send_$en;
  assign output_units_$0$recv_$msg = switch_units_$0$send_$msg;
  assign switch_units_$0$send_$rdy = output_units_$0$recv_$rdy;
  assign send_$0_$en = output_units_$0$send_$en;
  assign send_$0_$msg = output_units_$0$send_$msg;
  assign output_units_$0$send_$rdy = send_$0_$rdy;
  assign output_units_$1$recv_$en = switch_units_$1$send_$en;
  assign output_units_$1$recv_$msg = switch_units_$1$send_$msg;
  assign switch_units_$1$send_$rdy = output_units_$1$recv_$rdy;
  assign send_$1_$en = output_units_$1$send_$en;
  assign send_$1_$msg = output_units_$1$send_$msg;
  assign output_units_$1$send_$rdy = send_$1_$rdy;
  assign output_units_$2$recv_$en = switch_units_$2$send_$en;
  assign output_units_$2$recv_$msg = switch_units_$2$send_$msg;
  assign switch_units_$2$send_$rdy = output_units_$2$recv_$rdy;
  assign send_$2_$en = output_units_$2$send_$en;
  assign send_$2_$msg = output_units_$2$send_$msg;
  assign output_units_$2$send_$rdy = send_$2_$rdy;
  assign output_units_$3$recv_$en = switch_units_$3$send_$en;
  assign output_units_$3$recv_$msg = switch_units_$3$send_$msg;
  assign switch_units_$3$send_$rdy = output_units_$3$recv_$rdy;
  assign send_$3_$en = output_units_$3$send_$en;
  assign send_$3_$msg = output_units_$3$send_$msg;
  assign output_units_$3$send_$rdy = send_$3_$rdy;
  assign output_units_$4$recv_$en = switch_units_$4$send_$en;
  assign output_units_$4$recv_$msg = switch_units_$4$send_$msg;
  assign switch_units_$4$send_$rdy = output_units_$4$recv_$rdy;
  assign send_$4_$en = output_units_$4$send_$en;
  assign send_$4_$msg = output_units_$4$send_$msg;
  assign output_units_$4$send_$rdy = send_$4_$rdy;

endmodule
