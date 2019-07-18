// Minor ALU Op Codes
// Add, Subtract
typedef enum logic [2:0] {
  e_add_op                               = 3'b000   // Add
  ,e_sub_op                              = 3'b001   // Subtract
  ,e_lsh_op                              = 3'b010   // Left Shift
  ,e_rsh_op                              = 3'b011   // Right Shift
  ,e_and_op                              = 3'b100   // Bit-wise AND
  ,e_or_op                               = 3'b101   // Bit-wise OR
  ,e_xor_op                              = 3'b110   // Bit-wise XOR
  ,e_neg_op                              = 3'b111   // Bit-wise negation (unary)
} bp_cce_inst_minor_alu_op_e;

// Minor Branch Op Codes
typedef enum logic [2:0] {
  e_bi_op                                = 3'b111   // Branch Immediate (Unconditiona

  ,e_beq_op                              = 3'b010   // Branch if A == B
  ,e_bne_op                              = 3'b011   // Branch if A != B

  ,e_blt_op                              = 3'b100   // Branch if A < B
  ,e_ble_op                              = 3'b101   // Branch if A <= B
} bp_cce_inst_minor_branch_op_e;
