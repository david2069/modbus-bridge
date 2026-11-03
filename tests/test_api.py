"""Tests for the REST API, against modbus-connection's mock. All values are made up."""

import asyncio

import pytest
from fastapi.testclient import TestClient
from modbus_connection import IllegalDataAddressError
from modbus_connection.encode import encode_string
from modbus_connection.mock import MockModbusUnit

from modbus_bridge.api import create_app, event_stream
from modbus_bridge.service import DeviceService

TOKEN = "test-token-not-secret"
AUTH = {"Authorization": f"Bearer {TOKEN}"}
M713 = 40070  # model 713 header, after SunS (2) and model 1 (68)


def load_device(unit: MockModbusUnit) -> None:
    common = [
        1,
        66,
        *encode_string("ExampleMaker", length=16),
        *encode_string("ExampleModel", length=16),
        *encode_string("", length=8),
        *encode_string("1.0.0", length=8),
        *encode_string("SN-PLACEHOLDER", length=16),
        1,
        0,
    ]
    # WHRtg, WHAvail, SoC, SoH (not implemented), Sta, WH_SF +1, Pct_SF -1
    battery = [713, 7, 1350, 600, 875, 0xFFFF, 1, 1, 0xFFFF]
    unit.holding[40000] = [0x5375, 0x6E53, *common, *battery, 0xFFFF, 0]


@pytest.fixture
def service(mock_modbus_unit: MockModbusUnit) -> DeviceService:
    load_device(mock_modbus_unit)
    service = DeviceService("unit1", mock_modbus_unit, interval=60, reads=1, read_interval=0)
    asyncio.run(service.setup())
    return service


@pytest.fixture
def client(service: DeviceService) -> TestClient:
    return TestClient(create_app({"unit1": service}, [TOKEN]))


def test_token_required_except_health(client: TestClient) -> None:
    assert client.get("/api/v1/health").status_code == 200
    assert client.get("/api/v1/devices").status_code == 401
    bad = {"Authorization": "Bearer wrong"}
    assert client.get("/api/v1/devices", headers=bad).status_code == 401
    assert client.get("/api/v1/devices", headers=AUTH).status_code == 200


def test_app_refuses_to_start_without_token(service: DeviceService) -> None:
    with pytest.raises(ValueError):
        create_app({"unit1": service}, [])


def test_device_list_and_detail(client: TestClient) -> None:
    [summary] = client.get("/api/v1/devices", headers=AUTH).json()
    assert summary["id"] == "unit1"
    assert summary["identity"]["manufacturer"] == "ExampleMaker"
    assert summary["identity"]["options"] is None
    detail = client.get("/api/v1/devices/unit1", headers=AUTH).json()
    assert [m["model_id"] for m in detail["chain"]] == [1, 713]
    assert "713.SoH" in detail["not_implemented"]
    assert client.get("/api/v1/devices/nope", headers=AUTH).status_code == 404


def test_points_snapshot(client: TestClient) -> None:
    body = client.get("/api/v1/devices/unit1/points", headers=AUTH).json()
    points = body["points"]
    assert "713.SoH" not in points  # not implemented: never published
    assert "1.Opt" not in points
    assert points["713.SoC"]["value"] == 87.5
    assert points["713.SoC"]["units"] == "Pct"
    assert points["713.Sta"]["value"] == {"value": 1, "name": "WARNING"}


def test_unavailable_is_null(
    client: TestClient, service: DeviceService, mock_modbus_unit: MockModbusUnit
) -> None:
    mock_modbus_unit.fail_read(M713, IllegalDataAddressError(2))
    asyncio.run(service.poll_once())
    soc = client.get("/api/v1/devices/unit1/points", headers=AUTH).json()["points"]["713.SoC"]
    assert soc["value"] is None
    assert soc["available"] is False


def test_event_stream_snapshot_then_changes(
    service: DeviceService, mock_modbus_unit: MockModbusUnit
) -> None:
    async def run() -> tuple[str, str]:
        stream = event_stream(service, keepalive=5)
        first = await anext(stream)
        mock_modbus_unit.holding[40000][M713 - 40000 + 4] = 900  # SoC -> 90.0
        await service.poll_once()
        second = await anext(stream)
        await stream.aclose()
        return first, second

    first, second = asyncio.run(run())
    assert first.startswith("event: snapshot\n")
    assert '"713.SoC"' in first
    assert second.startswith("event: change\n")
    assert '"key": "713.SoC"' in second and '"value": 90.0' in second
