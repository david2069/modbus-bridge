"""Tests for checking the device again after a reconnect (design Q3, rule 8). Values are made up."""

import asyncio
import logging

import pytest
from fastapi.testclient import TestClient
from modbus_connection import ModbusConnectionError
from modbus_connection.encode import encode_string
from modbus_connection.mock import MockModbusUnit
from test_api import AUTH, TOKEN
from test_quirks import q, quirk_set

from modbus_bridge import service as service_module
from modbus_bridge.api import create_app
from modbus_bridge.quirks import QuirkSet
from modbus_bridge.service import DeviceService

FIRMWARE_2 = quirk_set(
    "firmware", {"manufacturer": "ExampleMaker", "firmware": {"min": "2.0.0"}},
    quirks=[q("fw2-soc", "713.SoC", label="Charge (firmware 2)")], set_id="test-fw2",
)  # fmt: skip


def load(unit: MockModbusUnit, version="1.0.0", serial="SN-PLACEHOLDER", battery=True) -> None:
    common = [
        1, 66,
        *encode_string("ExampleMaker", length=16),
        *encode_string("ExampleModel", length=16),
        *encode_string("", length=8),
        *encode_string(version, length=8),
        *encode_string(serial, length=16),
        1, 0,
    ]  # fmt: skip
    battery_model = [713, 7, 1350, 600, 875, 0xFFFF, 1, 1, 0xFFFF] if battery else []
    unit.holding[40000] = [0x5375, 0x6E53, *common, *battery_model, 0xFFFF, 0]


@pytest.fixture
def setup(mock_modbus_unit: MockModbusUnit, mock_modbus_connection, monkeypatch):
    load(mock_modbus_unit)
    calls = []
    original = service_module.discover

    async def counting(unit):
        calls.append(1)
        return await original(unit)

    monkeypatch.setattr(service_module, "discover", counting)
    service = DeviceService(
        "unit1", mock_modbus_unit, interval=60, reads=1, read_interval=0,
        quirk_sets=[QuirkSet.from_json(FIRMWARE_2)],
    )  # fmt: skip
    asyncio.run(service.setup())
    calls.clear()
    return service, mock_modbus_unit, mock_modbus_connection, calls


def poll(service: DeviceService) -> None:
    asyncio.run(service.poll_once())


def value(service: DeviceService, key: str):
    return service.poller.snapshot[key].value


def test_no_check_while_the_link_stays_up(setup) -> None:
    service, _, _, calls = setup
    poll(service)
    poll(service)
    assert calls == []
    assert value(service, "713.SoC") == 87.5


def test_lost_connection_unchanged_checks_once(setup) -> None:
    service, _, conn, calls = setup
    conn.simulate_connection_lost()
    poll(service)
    poll(service)
    assert len(calls) == 1
    assert service.refused is None
    assert value(service, "713.SoC") == 87.5


def test_changed_serial_refuses_the_device(setup, caplog) -> None:
    service, unit, conn, _ = setup
    load(unit, serial="SN-OTHER")
    conn.simulate_connection_lost()
    with caplog.at_level(logging.ERROR):
        poll(service)
        unit.read_events.clear()
        poll(service)
    assert unit.read_events == []  # not read again
    assert "SN-OTHER" in service.refused and "SN-PLACEHOLDER" in service.refused
    assert all(s.value is None for s in service.poller.snapshot.values())
    assert sum("refused" in r.getMessage() for r in caplog.records) == 1
    client = TestClient(create_app({"unit1": service}, [TOKEN]))
    body = client.get("/api/v1/devices/unit1", headers=AUTH).json()
    assert body["refused"] == service.refused
    assert body["last_error"] == service.refused


def test_changed_firmware_rebuilds_quirks(setup) -> None:
    service, unit, conn, _ = setup
    assert service.poller.snapshot["713.SoC"].label != "Charge (firmware 2)"
    load(unit, version="2.0.0")
    conn.simulate_connection_lost()
    poll(service)
    assert service.device.identity.version == "2.0.0"
    assert service.refused is None
    state = service.poller.snapshot["713.SoC"]
    assert (state.label, state.value) == ("Charge (firmware 2)", 87.5)
    assert "fw2-soc" in state.quirks


def test_changed_chain_is_read_again_and_points_removed(setup) -> None:
    service, unit, conn, _ = setup
    load(unit, battery=False)
    conn.simulate_connection_lost()
    poll(service)
    assert "713.SoC" not in service.poller.snapshot
    assert "713.SoC" in service.poller.removed
    assert [m.model_id for m in service.device.chain] == [1]


def test_failed_check_makes_points_unavailable_and_retries(setup) -> None:
    service, unit, conn, calls = setup
    conn.simulate_connection_lost()
    unit.fail_requests(ModbusConnectionError("down"))
    poll(service)
    assert value(service, "713.SoC") is None
    assert "not checked" in service.poller.last_error
    unit.fail_requests(None)
    poll(service)
    assert len(calls) == 2
    assert value(service, "713.SoC") == 87.5


def test_failed_poll_makes_a_check_due(setup) -> None:
    service, unit, _, calls = setup
    unit.fail_requests(ModbusConnectionError("down"))
    poll(service)  # fails without the callback firing
    assert calls == []
    unit.fail_requests(None)
    poll(service)
    assert len(calls) == 1
    assert value(service, "713.SoC") == 87.5
