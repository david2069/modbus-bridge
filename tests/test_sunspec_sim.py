"""Tests for the test-only SunSpec simulator, and modbus-bridge against it over real TCP."""

import asyncio
import importlib.util
import socket
import struct
from pathlib import Path

import pytest
from modbus_connection import ModbusTcpParams
from modbus_connection.tmodbus import ModbusConnection

from modbus_bridge.implemented import discover_implemented
from modbus_bridge.sunspec import discover

_PATH = Path(__file__).parent.parent / "scripts" / "sunspec_sim.py"
_SPEC = importlib.util.spec_from_file_location("sunspec_sim", _PATH)
assert _SPEC and _SPEC.loader
sim = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(sim)


@pytest.mark.parametrize(
    ("sunspec_type", "size", "value", "regs"),
    [
        ("int16", 1, -5, [0xFFFB]),
        ("int16", 1, None, [0x8000]),
        ("sunssf", 1, -2, [0xFFFE]),
        ("uint16", 1, None, [0xFFFF]),
        ("enum16", 1, 4, [4]),
        ("acc32", 2, 70000, [1, 4464]),
        ("acc32", 2, None, [0, 0]),
        ("uint32", 2, None, [0xFFFF, 0xFFFF]),
        ("int32", 2, None, [0x8000, 0]),
        ("bitfield32", 2, None, [0xFFFF, 0xFFFF]),
        ("float32", 2, None, [0x7FC0, 0]),
        ("string", 2, "AB", [0x4142, 0]),
        ("string", 2, None, [0, 0]),
        ("pad", 1, None, [0x8000]),
    ],
)
def test_encode(sunspec_type: str, size: int, value: object, regs: list[int]) -> None:
    assert sim.encode(sunspec_type, size, value) == regs


def test_string_too_long_is_refused() -> None:
    with pytest.raises(ValueError, match="longer"):
        sim.encode("string", 1, "ABC")


def test_model_length_matches_its_definition() -> None:
    regs = sim.build_map(sim.inverter_models(0.0))
    assert regs[:2] == [0x5375, 0x6E53]
    assert regs[2:4] == [1, 66]
    assert regs[-2:] == [0xFFFF, 0]


def test_answer_errors() -> None:
    server = sim.SunSpecSimulator(sim.inverter_models)
    assert server.answer(1, bytes([6, 0x9C, 0x40, 0, 1])) == bytes([0x86, 1])
    assert server.answer(1, struct.pack(">BHH", 3, 39999, 1)) == bytes([0x83, 2])
    assert server.answer(1, struct.pack(">BHH", 3, 40000, 126)) == bytes([0x83, 3])
    sun_s = bytes([3, 4, 0x53, 0x75, 0x6E, 0x53])
    assert server.answer(1, struct.pack(">BHH", 3, 40000, 2)) == sun_s


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_end_to_end_over_tcp() -> None:
    async def run():
        port = _free_port()
        server = await sim.SunSpecSimulator(sim.inverter_models).start("127.0.0.1", port)
        connection = ModbusConnection(ModbusTcpParams(host="127.0.0.1", port=port), timeout=5)
        try:
            await connection.connect()
            unit = connection.for_unit(1)
            device = await discover(unit)
            found, _ = await discover_implemented(unit, device.chain, 2, 0.0)
            with pytest.raises(Exception, match="Exception 0x02"):
                await unit.read_holding_registers(30000, 1)
            return device, found
        finally:
            await connection.close()
            server.close()
            await server.wait_closed()

    device, found = asyncio.run(run())
    assert device.base_address == 40000
    assert device.identity.manufacturer == "ExampleSolar"
    assert device.identity.serial == "SIM-0000-0001"
    assert device.identity.options is None
    assert [m.model_id for m in device.chain] == [1, 103, 120, 160]
    assert {"103.W", "103.WH", "120.WRtg", "160.module[2].DCW"} <= found.implemented
    assert {"103.TmpSnk", "120.WHRtg", "160.TmsPer", "160.module[1].Tmp"} <= found.not_implemented
