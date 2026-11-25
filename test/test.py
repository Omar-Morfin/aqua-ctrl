import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer


@cocotb.test()
async def test_project(dut):

    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Reinicio del sistema
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    await ClockCycles(dut.clk, 10)

    dut.rst_n.value = 1

    async def comprobar(entrada, esperado, mensaje):

        dut.ui_in.value = entrada

        await ClockCycles(dut.clk, 3)
        await Timer(1, unit="us")

        resultado = int(dut.uo_out.value)

        assert resultado == esperado, (
            f"{mensaje}: esperado={esperado}, "
            f"obtenido={resultado}"
        )

        dut._log.info(f"CORRECTO: {mensaje}")

    # Prueba 1: Tanque debajo del minimo
    await comprobar(
        0b00001100,
        0b00000011,
        "Encendido de bomba"
    )

    # Prueba 2: Nivel intermedio durante llenado
    await comprobar(
        0b00001101,
        0b00000001,
        "Bomba continua encendida"
    )

    # Prueba 3: Tanque lleno
    await comprobar(
        0b00001111,
        0b00000100,
        "Bomba apagada por tanque lleno"
    )

    # Prueba 4: Nivel intermedio durante vaciado
    await comprobar(
        0b00001101,
        0b00000000,
        "Bomba permanece apagada"
    )

    # Prueba 5: Falta de agua en cisterna
    await comprobar(
        0b00001000,
        0b00010010,
        "Bloqueo por falta de agua"
    )

    # Prueba 6: Sensores contradictorios
    await comprobar(
        0b00001110,
        0b00011000,
        "Alarma por falla de sensores"
    )

    # Prueba 7: Memoria de alarma
    await comprobar(
        0b00001100,
        0b00011010,
        "Alarma permanece activa"
    )

    # Prueba 8: Reinicio de alarma
    await comprobar(
        0b00011100,
        0b00000011,
        "Alarma eliminada y bomba habilitada"
    )

    # Prueba 9: Sistema deshabilitado
    await comprobar(
        0b00000100,
        0b00010010,
        "Sistema deshabilitado"
    )

    dut._log.info("TODAS LAS PRUEBAS COMPLETADAS")
