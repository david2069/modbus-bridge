"""Tests for removing a point a quirk takes away (design Q4, U7). All values are made up."""

import asyncio
import json
from pathlib import Path

import httpx
from modbus_connection import IllegalDataAddressError
from modbus_connection.mock import MockModbusUnit
from test_api import AUTH
from test_mqtt_publisher import DETAIL, point
from test_poller import make_poller, setup_unit
from test_user_quirks import BASE, make, points, poll, reading

from modbus_bridge.api import event_stream
from modbus_bridge.mqtt import follow
from modbus_bridge.mqtt_publisher import DiscoveryPublisher


def add_reading(client) -> None:
    answer = client.put(f"{BASE}/user-quirks/reading/u-r-a", headers=AUTH,
                        json=reading("u-r-a", 1000, "a"))  # fmt: skip
    assert answer.status_code == 200


def test_point_no_longer_built_is_removed(mock_modbus_unit: MockModbusUnit, tmp_path: Path) -> None:
    service, client = make(mock_modbus_unit, tmp_path)
    add_reading(client)
    poll(service)
    assert "raw.a" in points(client)
    assert service.poller.removed == []
    client.delete(f"{BASE}/user-quirks/reading/u-r-a", headers=AUTH)
    poll(service)
    assert service.poller.removed == ["raw.a"]
    assert "raw.a" not in points(client)
    poll(service)
    assert service.poller.removed == []  # only reported once


def test_failed_read_is_not_removed(mock_modbus_unit: MockModbusUnit) -> None:
    setup_unit(mock_modbus_unit)
    poller = make_poller(mock_modbus_unit)
    asyncio.run(poller.poll())
    mock_modbus_unit.fail_read(40000, IllegalDataAddressError(2))
    asyncio.run(poller.poll())
    assert poller.removed == []
    assert poller.snapshot["713.SoC"].value is None


def test_removal_alone_reaches_subscribers_and_stream(
    mock_modbus_unit: MockModbusUnit, tmp_path: Path
) -> None:
    service, client = make(mock_modbus_unit, tmp_path)
    add_reading(client)
    poll(service)
    client.delete(f"{BASE}/user-quirks/reading/u-r-a", headers=AUTH)

    async def run() -> tuple[str, int]:
        stream = event_stream(service, keepalive=5)
        await anext(stream)  # the snapshot
        before = service.sequence
        changes = await service.poll_once()
        assert changes == []  # nothing changed value, one point removed
        event = await anext(stream)
        await stream.aclose()
        return event, service.sequence - before

    event, step = asyncio.run(run())
    assert step == 1
    assert event == f'event: removed\nid: {service.sequence}\ndata: {{"key": "raw.a"}}\n\n'


def test_publisher_remove_messages() -> None:
    publisher = DiscoveryPublisher(DETAIL)
    config = publisher.discovery(point("label.mode", "x"))
    state = publisher.state(point("label.mode", "x"))
    removal = publisher.remove("label.mode")
    assert [m.topic for m in removal] == [config.topic, *(m.topic for m in state)]
    assert all(m.payload == "" and m.retain for m in removal)


class FakeMqtt:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    async def publish(self, topic: str, payload: str, qos: int, retain: bool) -> None:
        self.sent.append((topic, payload))


def test_point_back_after_removal_gets_discovery_again() -> None:
    publisher = DiscoveryPublisher(DETAIL)
    mode = point("label.mode", "x")
    body = "".join([
        f"event: snapshot\nid: 1\ndata: {json.dumps({'points': {'label.mode': mode}})}\n\n",
        'event: removed\nid: 2\ndata: {"key": "label.mode"}\n\n',
        f"event: change\nid: 3\ndata: {json.dumps(mode)}\n\n",
    ])  # fmt: skip
    transport = httpx.MockTransport(lambda request: httpx.Response(200, text=body))
    mqtt = FakeMqtt()

    async def run() -> None:
        async with httpx.AsyncClient(transport=transport) as http:
            await follow(mqtt, http, publisher, "http://api.invalid", "unit1")

    asyncio.run(run())
    config_topic = publisher.discovery(mode).topic
    configs = [payload for topic, payload in mqtt.sent if topic == config_topic]
    assert len(configs) == 3
    assert configs[0] and configs[1] == "" and json.loads(configs[2])["unique_id"]
