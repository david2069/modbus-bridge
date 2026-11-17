"""Tests for reading any register on request (P2 step 22, design S5). Values are made up."""

import asyncio

import pytest
from fastapi.testclient import TestClient
from modbus_connection import IllegalDataAddressError, ModbusTimeoutError
from modbus_connection.mock import MockModbusUnit
from test_api import AUTH, TOKEN, client, load_device, service  # noqa: F401 (fixtures)

from modbus_bridge.api import create_app
from modbus_bridge.service import DeviceService

URL = "/api/v1/devices/unit1/registers"


def _reads(unit: MockModbusUnit) -> int:
    return len(unit.read_events)


def test_holding_and_input_words_as_stored(
    client: TestClient,  # noqa: F811
    mock_modbus_unit: MockModbusUnit,
) -> None:
    mock_modbus_unit.holding[5000] = [1, 0xFFFF, 0x8000, 7]
    mock_modbus_unit.input[300] = [42, 43]
    answer = client.get(URL, params={"address": 5001, "count": 3}, headers=AUTH).json()
    assert answer == {"device": "unit1", "table": "holding", "address": 5001, "count": 3,
                      "registers": [0xFFFF, 0x8000, 7]}  # fmt: skip
    answer = client.get(URL, params={"address": 300, "count": 2, "table": "input"}, headers=AUTH)
    assert answer.json()["registers"] == [42, 43]
    sun_s = client.get(URL, params={"address": 40000, "count": 2}, headers=AUTH).json()
    assert sun_s["registers"] == [0x5375, 0x6E53]


def test_default_is_one_holding_register(
    client: TestClient,  # noqa: F811
    mock_modbus_unit: MockModbusUnit,
) -> None:
    mock_modbus_unit.holding[6000] = [9, 10]
    answer = client.get(URL, params={"address": 6000}, headers=AUTH).json()
    assert (answer["table"], answer["count"], answer["registers"]) == ("holding", 1, [9])


@pytest.mark.parametrize(
    "params",
    [{"address": -1}, {"address": 65536}, {"address": 0, "count": 0},
     {"address": 0, "count": 126}, {"address": 65500, "count": 37},
     {"address": 0, "table": "coil"}, {"address": "x"}, {}],
)  # fmt: skip
def test_bad_requests_are_refused_and_nothing_is_read(
    client: TestClient,  # noqa: F811
    mock_modbus_unit: MockModbusUnit,
    params: dict,
) -> None:
    before = _reads(mock_modbus_unit)
    assert client.get(URL, params=params, headers=AUTH).status_code == 422
    assert _reads(mock_modbus_unit) == before


def test_last_register_can_be_read(
    client: TestClient,  # noqa: F811
    mock_modbus_unit: MockModbusUnit,
) -> None:
    mock_modbus_unit.holding[65535] = [3]
    answer = client.get(URL, params={"address": 65535}, headers=AUTH)
    assert answer.json()["registers"] == [3]


def test_modbus_exception_is_502_never_zeros(
    client: TestClient,  # noqa: F811
    mock_modbus_unit: MockModbusUnit,
) -> None:
    mock_modbus_unit.fail_read(7000, IllegalDataAddressError(2))
    answer = client.get(URL, params={"address": 7000}, headers=AUTH)
    assert answer.status_code == 502
    assert "IllegalDataAddressError" in answer.json()["detail"]
    assert "registers" not in answer.json()


def test_timeout_is_503(
    client: TestClient,  # noqa: F811
    mock_modbus_unit: MockModbusUnit,
) -> None:
    mock_modbus_unit.fail_requests(ModbusTimeoutError("no answer"))
    answer = client.get(URL, params={"address": 40000}, headers=AUTH)
    assert answer.status_code == 503
    assert "ModbusTimeoutError" in answer.json()["detail"]


def test_not_ready_device_is_503_and_nothing_is_read(mock_modbus_unit: MockModbusUnit) -> None:
    load_device(mock_modbus_unit)
    svc = DeviceService("unit1", mock_modbus_unit, interval=60, reads=1, read_interval=0)
    app = TestClient(create_app({"unit1": svc}, [TOKEN]))
    answer = app.get(URL, params={"address": 40000}, headers=AUTH)
    assert answer.status_code == 503
    assert _reads(mock_modbus_unit) == 0


@pytest.mark.parametrize("state", ["refused", "recheck"])
def test_refused_or_unchecked_device_is_503_and_nothing_is_read(
    service: DeviceService,  # noqa: F811
    mock_modbus_unit: MockModbusUnit,
    state: str,
) -> None:
    if state == "refused":
        service.refused = "another device answers at this address"
    else:
        service._recheck = True  # the link was lost; the next poll checks the device
    app = TestClient(create_app({"unit1": service}, [TOKEN]))
    before = _reads(mock_modbus_unit)
    answer = app.get(URL, params={"address": 40000}, headers=AUTH)
    assert answer.status_code == 503
    assert _reads(mock_modbus_unit) == before


def test_token_needed_and_unknown_device(client: TestClient) -> None:  # noqa: F811
    assert client.get(URL, params={"address": 0}).status_code == 401
    other = "/api/v1/devices/nope/registers"
    assert client.get(other, params={"address": 0}, headers=AUTH).status_code == 404


def test_read_waits_for_the_poll_lock(
    service: DeviceService,  # noqa: F811
    mock_modbus_unit: MockModbusUnit,
) -> None:
    mock_modbus_unit.holding[8000] = [11]

    async def run() -> None:
        async with service._poll_lock:
            task = asyncio.create_task(service.read_registers("holding", 8000, 1))
            await asyncio.sleep(0.05)
            assert not task.done()  # held back while a poll has the connection
            before = _reads(mock_modbus_unit)
        assert await task == [11]
        assert _reads(mock_modbus_unit) == before + 1

    asyncio.run(run())
