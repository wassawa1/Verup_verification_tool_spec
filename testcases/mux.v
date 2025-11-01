// 8-to-1 Multiplexer
module mux_8to1 (
    input [7:0] in,
    input [2:0] sel,
    output out
);
    assign out = in[sel];
endmodule

module testbench_mux;
    reg [7:0] in;
    reg [2:0] sel;
    wire out;
    integer i, j;
    
    mux_8to1 dut(.in(in), .sel(sel), .out(out));
    
    initial begin
        $dumpfile("mux.vcd");
        $dumpvars(0, testbench_mux);
        
        // Test all input patterns and selections
        for (i = 0; i < 256; i = i + 1) begin
            in = i;
            for (j = 0; j < 8; j = j + 1) begin
                sel = j;
                #3;
            end
        end
        
        $finish;
    end
endmodule
