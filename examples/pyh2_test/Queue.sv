/*========================================================================
  NormalQueue
 *======================================================================
  System verilog implementation of a register based normal queue.

  Author : Yanghui Ou
    Date : June 9, 2019
*/

module Queue
#(
  // Parameters
  parameter p_data_width  = 32,
  parameter p_num_entries = 2,
  // Internal derived parameters
  parameter c_count_width = $clog2( p_num_entries+1 )
)
(
  input  logic                     clk,
  input  logic                     reset,
  output logic [c_count_width-1:0] count,
  input  logic                     deq_en,
  output logic                     deq_rdy,
  output logic [p_data_width -1:0] deq_msg,
  input  logic                     enq_en,
  output logic                     enq_rdy,
  input  logic [p_data_width -1:0] enq_msg
);

  localparam addr_width = p_num_entries == 1 ? 1 : $clog2( p_num_entries );
  localparam [c_count_width-1:0] max_size = p_num_entries[c_count_width-1:0];
  localparam [addr_width   -1:0] last_idx = p_num_entries[addr_width -1:0] - 'd1;

  // Wire declaration
  logic [p_data_width-1 :0] data_reg [0:p_num_entries-1];
  logic [addr_width-1   :0] deq_ptr;
  logic [addr_width-1   :0] enq_ptr;
  logic [addr_width-1   :0] deq_ptr_next;
  logic [addr_width-1   :0] enq_ptr_next;
  logic [c_count_width-1:0] count_next;

  // Sequential logic
  always_ff @(posedge clk) begin
    if (reset) begin
      deq_ptr <= 'd0;
      deq_ptr <= 'd0;
      count   <= 'd0;
    end
    else begin
      // TODO: separate comb logic
      deq_ptr <= deq_ptr_next;
      enq_ptr <= enq_ptr_next;
      count   <= count_next;
    end
  end

  always_ff @(posedge clk) begin
    if (enq_en) begin
      data_reg[enq_ptr] <= enq_msg;
    end
  end

  assign deq_ptr_next = ~deq_en ? deq_ptr :
                         deq_ptr == last_idx ? 'd0 : deq_ptr + 'd1;
  assign enq_ptr_next = ~enq_en ? enq_ptr :
                         enq_ptr == last_idx ? 'd0 : enq_ptr + 'd1;
  assign count_next = enq_en & ~deq_en ? count + 'd1 :
                      deq_en & ~enq_en ? count - 'd1 : count;

  assign enq_rdy = count < max_size;
  assign deq_rdy = count > 'd0;
  assign deq_msg = data_reg[deq_ptr];

endmodule
