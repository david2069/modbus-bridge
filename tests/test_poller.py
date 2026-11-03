"""Tests for the poller, against modbus-connection's mock. All values are made up."""

import asyncio

from modbus_connection import IllegalDataAddressError, ModbusConnectionError
from modbus_connection.mock import MockModbusUnit
from modbus_connection.model.sunspec import SunSpecModel

from modbus_bridge.implemented import ImplementedPoints
from modbus_bridge.poller import Poller

CHAIN = [SunSpecModel(model_id=713, address=40000, length=7)]
SOC = 40004


def setup_unit(unit: MockModbusUnit) -> None:
    # WHRtg, WHAvail, SoC, SoH (not implemented), Sta, WH_SF +1, Pct_SF -1
    unit.holding[40000] = [713, 7, 1350, 600, 875, 0xFFFF, 0, 1, 0xFFFF]


def make_poller(unit: MockModbusUnit) -> Poller:
    implemented = ImplementedPoints(
        source="test",
        implemented=frozenset({"713.WHRtg", "713.WHAvail", "713.SoC", "713.Sta"}),
        not_implemented=frozenset({"713.SoH"}),
        unreadable_models=(),
    )
    return Poller(unit, CHAIN, implemented)


def keys(states) -> list[str]:
    return [s.key for s in states]


def test_first_poll_then_only_changes(mock_modbus_unit: MockModbusUnit) -> None:
    setup_unit(mock_modbus_unit)
    poller = make_poller(mock_modbus_unit)

    first = asyncio.run(poller.poll())
    assert keys(first) == ["713.SoC", "713.Sta", "713.WHAvail", "713.WHRtg"]
    assert "713.SoH" not in poller.snapshot  # not implemented: never shown
    assert asyncio.run(poller.poll()) == []

    mock_modbus_unit.holding[40000][4] = 900  # SoC 87.5 -> 90.0
    changed = asyncio.run(poller.poll())
    assert keys(changed) == ["713.SoC"]
    assert changed[0].value == 90.0


def test_refused_model_unavailable_then_back(mock_modbus_unit: MockModbusUnit) -> None:
    setup_unit(mock_modbus_unit)
    poller = make_poller(mock_modbus_unit)
    asyncio.run(poller.poll())

    mock_modbus_unit.fail_read(40000, IllegalDataAddressError(2))
    down = asyncio.run(poller.poll())
    assert len(down) == 4 and all(s.value is None for s in down)
    assert all(not s.available for s in poller.snapshot.values())

    mock_modbus_unit.fail_read(40000, None)
    back = asyncio.run(poller.poll())
    assert len(back) == 4 and all(s.available for s in back)


def test_lost_connection_makes_everything_unavailable(mock_modbus_unit: MockModbusUnit) -> None:
    setup_unit(mock_modbus_unit)
    poller = make_poller(mock_modbus_unit)
    asyncio.run(poller.poll())

    mock_modbus_unit.fail_requests(ModbusConnectionError("link down"))
    down = asyncio.run(poller.poll())
    assert len(down) == 4 and all(s.value is None for s in down)
    assert poller.last_error and "link down" in poller.last_error

    mock_modbus_unit.fail_requests(None)
    assert len(asyncio.run(poller.poll())) == 4
    assert poller.last_error is None


def test_point_that_starts_giving_a_value_is_promoted(mock_modbus_unit: MockModbusUnit) -> None:
    setup_unit(mock_modbus_unit)
    poller = make_poller(mock_modbus_unit)
    asyncio.run(poller.poll())

    mock_modbus_unit.holding[40000][5] = 970  # SoH now 97.0
    changed = asyncio.run(poller.poll())
    assert keys(changed) == ["713.SoH"]
    assert "713.SoH" in poller.implemented.implemented
    assert poller.snapshot["713.SoH"].value == 97.0
