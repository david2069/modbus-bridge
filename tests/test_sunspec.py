"""Unit tests for SunSpec discovery, against modbus-connection's in-memory mock.

All names and values here are placeholders, not taken from any real device.
"""

import asyncio

import pytest
from modbus_connection.encode import encode_string
from modbus_connection.mock import MockModbusUnit
from modbus_connection.model.sunspec import SunSpecError

from modbus_bridge.probe import NOT_SET, format_device
from modbus_bridge.sunspec import discover

SUNS = [0x5375, 0x6E53]  # "SunS"
END = [0xFFFF, 0]


def common_model(
    mn: str = "ExampleMaker",
    md: str = "ExampleModel",
    opt: str = "",
    vr: str = "1.0.0",
    sn: str = "SN-PLACEHOLDER",
    da: int = 1,
) -> list[int]:
    """Model 1 block: header plus 66 data registers."""
    return [
        1,
        66,
        *encode_string(mn, length=16),
        *encode_string(md, length=16),
        *encode_string(opt, length=8),
        *encode_string(vr, length=8),
        *encode_string(sn, length=16),
        da,
        0,  # Pad
    ]


def chain_at(unit: MockModbusUnit, base: int, *blocks: list[int]) -> None:
    unit.holding[base] = [*SUNS, *[word for block in blocks for word in block], *END]


def test_discover_at_40000(mock_modbus_unit: MockModbusUnit) -> None:
    chain_at(mock_modbus_unit, 40000, common_model(), [701, 4, 0, 0, 0, 0])
    device = asyncio.run(discover(mock_modbus_unit))

    assert device.base_address == 40000
    assert device.identity.manufacturer == "ExampleMaker"
    assert device.identity.model == "ExampleModel"
    assert device.identity.version == "1.0.0"
    assert device.identity.serial == "SN-PLACEHOLDER"
    assert device.identity.device_address == 1
    assert [(m.model_id, m.address, m.length) for m in device.chain] == [
        (1, 40002, 66),
        (701, 40070, 4),
    ]


def test_empty_string_is_missing(mock_modbus_unit: MockModbusUnit) -> None:
    chain_at(mock_modbus_unit, 40000, common_model(opt=""))
    device = asyncio.run(discover(mock_modbus_unit))

    assert device.identity.options is None
    assert f"Opt {NOT_SET}" in format_device(device)


def test_falls_back_to_base_0(mock_modbus_unit: MockModbusUnit) -> None:
    chain_at(mock_modbus_unit, 0, common_model())
    device = asyncio.run(discover(mock_modbus_unit))

    assert device.base_address == 0
    assert device.chain[0].model_id == 1


def test_no_sunspec_raises(mock_modbus_unit: MockModbusUnit) -> None:
    with pytest.raises(SunSpecError, match="No SunSpec chain found"):
        asyncio.run(discover(mock_modbus_unit))


def test_chain_without_model_1_raises(mock_modbus_unit: MockModbusUnit) -> None:
    chain_at(mock_modbus_unit, 40000, [701, 4, 0, 0, 0, 0])
    with pytest.raises(SunSpecError, match="no Model 1"):
        asyncio.run(discover(mock_modbus_unit))
