// Simple 4-bit Adder with Carry
module adder_4bit (
    input [3:0] a,
    input [3:0] b,
    input cin,
    output [3:0] sum,
    output cout
);
    assign {cout, sum} = a + b + cin;
endmodule

module testbench_adder;
    reg [3:0] a, b;
    reg cin;
    wire [3:0] sum;
    wire cout;
    integer i, j;
    
    adder_4bit dut(.a(a), .b(b), .cin(cin), .sum(sum), .cout(cout));
    
    initial begin
        $dumpfile("adder.vcd");
        $dumpvars(0, testbench_adder);
        
        // Test all combinations
        for (i = 0; i < 16; i = i + 1) begin
            for (j = 0; j < 16; j = j + 1) begin
                a = i;
                b = j;
                cin = 0;
                #5;
                cin = 1;
                #5;
            end
        end
        
        $finish;
    end
endmodule
