// Simple 8-bit Register with Read/Write
module memory_reg (
    input clk,
    input we,
    input [2:0] addr,
    input [7:0] din,
    output [7:0] dout
);
    reg [7:0] mem [7:0];  // 8 registers of 8 bits each
    
    assign dout = mem[addr];
    
    always @(posedge clk) begin
        if (we)
            mem[addr] <= din;
    end
endmodule

module testbench_mem;
    reg clk, we;
    reg [2:0] addr;
    reg [7:0] din;
    wire [7:0] dout;
    integer i, j;
    
    memory_reg dut(.clk(clk), .we(we), .addr(addr), .din(din), .dout(dout));
    
    initial begin
        $dumpfile("mem.vcd");
        $dumpvars(0, testbench_mem);
        
        clk = 0;
        forever #5 clk = ~clk;
    end
    
    initial begin
        we = 0;
        addr = 0;
        din = 0;
        
        // Write all locations
        for (i = 0; i < 8; i = i + 1) begin
            we = 1;
            addr = i;
            din = i * 16 + 5;  // Distinctive pattern
            @(posedge clk);
        end
        
        we = 0;
        
        // Read all locations
        for (i = 0; i < 8; i = i + 1) begin
            addr = i;
            #10;
        end
        
        #20;
        $finish;
    end
endmodule
