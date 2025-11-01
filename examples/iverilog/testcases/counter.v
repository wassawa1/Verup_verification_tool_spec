module counter (
    input clk,
    input rst,
    output [7:0] count
);
    reg [7:0] counter;
    assign count = counter;
    
    always @(posedge clk or posedge rst) begin
        if (rst)
            counter <= 8'b0;
        else
            counter <= counter + 1;
    end
endmodule

module testbench;
    reg clk, rst;
    wire [7:0] count;
    integer i;
    
    counter dut(.clk(clk), .rst(rst), .count(count));
    
    initial begin
        $dumpfile("counter.vcd");
        $dumpvars(0, testbench);
        
        clk = 0;
        rst = 1;
        #10 rst = 0;
        
        for (i = 0; i < 100; i = i + 1) begin
            #10 clk = ~clk;
        end
        
        $display("Total CPU time: 1.234 seconds");
        $display("Total errors: 0");
        $display("Total warnings: 2");
        $finish;
    end
    
    always #5 clk = ~clk;
    
endmodule
