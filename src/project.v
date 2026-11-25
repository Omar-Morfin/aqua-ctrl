`default_nettype none

module tt_um_aqua_ctrl (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);

    // Entradas digitales
    wire nivel_min    = ui_in[0];
    wire nivel_max    = ui_in[1];
    wire agua_disp    = ui_in[2];
    wire habilitado   = ui_in[3];
    wire reset_alarma = ui_in[4];

    // Variables internas
    reg bomba;
    reg alarma;

    // Deteccion de fallas
    wire falla_sensor = nivel_max && !nivel_min;

    wire bloqueo = !agua_disp || !habilitado ||
                   alarma || falla_sensor || !ena;

    // Control automatico
    always @(posedge clk or negedge rst_n) begin

        if (!rst_n) begin
            bomba  <= 1'b0;
            alarma <= 1'b0;
        end

        else begin

            // Memoria de alarma
            if (falla_sensor)
                alarma <= 1'b1;

            else if (reset_alarma)
                alarma <= 1'b0;

            // Control de la bomba
            if (bloqueo)
                bomba <= 1'b0;

            else if (nivel_max)
                bomba <= 1'b0;

            else if (!nivel_min)
                bomba <= 1'b1;

            // Nivel intermedio:
            // conserva el estado de la bomba

        end
    end

    // Salidas digitales
    assign uo_out[0] = bomba && !bloqueo &&
                       !nivel_max && rst_n;

    assign uo_out[1] = !nivel_min && !falla_sensor;

    assign uo_out[2] = nivel_max && !falla_sensor;

    assign uo_out[3] = alarma || falla_sensor;

    assign uo_out[4] = bloqueo || !rst_n;

    assign uo_out[7:5] = 3'b000;

    // Pines bidireccionales sin utilizar
    assign uio_out = 8'b00000000;
    assign uio_oe  = 8'b00000000;

    // Entradas sin utilizar
    wire _unused = &{ui_in[7:5], uio_in, 1'b0};

endmodule
