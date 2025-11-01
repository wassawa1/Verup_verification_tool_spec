// Finite State Machine - Traffic Light Controller
module traffic_light (
    input clk,
    input rst,
    output [2:0] light  // 3'b100=Red, 3'b010=Green, 3'b001=Yellow
);
    reg [2:0] state;
    parameter RED = 3'b100, GREEN = 3'b010, YELLOW = 3'b001;
    parameter RED_TIME = 20, GREEN_TIME = 15, YELLOW_TIME = 5;
    
    reg [7:0] counter;
    
    assign light = state;
    
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            state <= RED;
            counter <= 0;
        end else begin
            if (counter >= RED_TIME && state == RED) begin
                state <= GREEN;
                counter <= 0;
            end else if (counter >= GREEN_TIME && state == GREEN) begin
                state <= YELLOW;
                counter <= 0;
            end else if (counter >= YELLOW_TIME && state == YELLOW) begin
                state <= RED;
                counter <= 0;
            end else begin
                counter <= counter + 1;
            end
        end
    end
endmodule

module testbench_fsm;
    reg clk, rst;
    wire [2:0] light;
    integer cycle;
    
    traffic_light dut(.clk(clk), .rst(rst), .light(light));
    
    initial begin
        $dumpfile("fsm.vcd");
        $dumpvars(0, testbench_fsm);
        
        clk = 0;
        forever #5 clk = ~clk;
    end
    
    initial begin
        rst = 1;
        #10;
        rst = 0;
        
        // Run for multiple cycles
        for (cycle = 0; cycle < 100; cycle = cycle + 1) begin
            @(posedge clk);
        end
        
        $finish;
    end
endmodule
