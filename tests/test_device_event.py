"""Tests for the device event: new firmware reaches HA without a restart. Values are made up."""

import asyncio
import json
from pathlib import Path

import httpx
import pytest
from test_mqtt_publisher import DETAIL, point
from test_publisher_lifecycle import AVAILABILITY, Broker, args, fast_retry  # noqa: F401
from test_recheck import load, setup  # noqa: F401 (fixture)
from test_removed import FakeMqtt

from modbus_bridge import mqtt
from modbus_bridge.api import event_stream
from modbus_bridge.mqtt import follow
from modbus_bridge.mqtt_publisher import DiscoveryPublisher, IdentityError
from modbus_bridge.service import DeviceChanged

V2 = DETAIL["identity"] | {"version": "2.0.0"}


def drain(queue: asyncio.Queue) -> list:
    items = []
    while not queue.empty():
        items.append(queue.get_nowait())
    return items


def test_firmware_change_sends_one_device_update_first(setup) -> None:  # noqa: F811
    service, unit, conn, _ = setup
    queue = service.subscribe()
    load(unit, version="2.0.0")
    conn.simulate_connection_lost()
    asyncio.run(service.poll_once())
    items = drain(queue)
    notices = [i for i in items if isinstance(i, DeviceChanged)]
    assert len(notices) == 1 and items[0] is notices[0]
    assert notices[0].identity["version"] == "2.0.0"
    assert notices[0].identity["serial"] == "SN-PLACEHOLDER"


def test_event_stream_sends_device_event(setup) -> None:  # noqa: F811
    service, unit, conn, _ = setup

    async def run() -> str:
        stream = event_stream(service, keepalive=5)
        await anext(stream)  # snapshot
        load(unit, version="2.0.0")
        conn.simulate_connection_lost()
        await service.poll_once()
        second = await anext(stream)
        await stream.aclose()
        return second

    second = asyncio.run(run())
    assert second.startswith("event: device\n")
    data = json.loads(second.split("data: ", 1)[1])
    assert data["identity"]["version"] == "2.0.0"


@pytest.mark.parametrize("serial", ["SN-PLACEHOLDER", "SN-OTHER"])
def test_no_device_update_when_unchanged_or_refused(setup, serial: str) -> None:  # noqa: F811
    service, unit, conn, _ = setup
    queue = service.subscribe()
    load(unit, serial=serial)
    conn.simulate_connection_lost()
    asyncio.run(service.poll_once())
    assert not any(isinstance(i, DeviceChanged) for i in drain(queue))
    assert (service.refused is not None) is (serial == "SN-OTHER")


def follow_events(publisher: DiscoveryPublisher, events: list) -> FakeMqtt:
    body = "".join(f"event: {e}\nid: {i}\ndata: {json.dumps(d)}\n\n" for i, (e, d) in
                   enumerate(events))  # fmt: skip
    transport = httpx.MockTransport(lambda request: httpx.Response(200, text=body))
    client = FakeMqtt()

    async def run() -> None:
        async with httpx.AsyncClient(transport=transport) as http:
            await follow(client, http, publisher, "http://api.invalid", "unit1")

    asyncio.run(run())
    return client


def test_device_event_resends_every_config_with_new_firmware() -> None:
    publisher = DiscoveryPublisher(DETAIL)
    a, b = point("label.a", 1), point("label.b", 2, units="W", sunspec_type="rule")
    snapshot = ("snapshot", {"points": {"label.a": a, "label.b": b}})
    before = follow_events(DiscoveryPublisher(DETAIL), [snapshot])
    client = follow_events(publisher, [snapshot, ("device", {"identity": V2})])
    after = client.sent[len(before.sent) :]
    configs = {t: json.loads(p) for t, p in after}
    assert len(after) == 2 and all(t.endswith("/config") for t, _ in after)
    assert {c["device"]["sw_version"] for c in configs.values()} == {"2.0.0"}
    assert configs[publisher.discovery(b).topic]["unit_of_measurement"] == "W"


def test_unchanged_device_event_sends_nothing() -> None:
    snapshot = ("snapshot", {"points": {"label.a": point("label.a", 1)}})
    before = follow_events(DiscoveryPublisher(DETAIL), [snapshot])
    client = follow_events(DiscoveryPublisher(DETAIL),
                           [snapshot, ("device", {"identity": DETAIL["identity"]})])  # fmt: skip
    assert client.sent == before.sent


def test_another_serial_stops_the_publisher() -> None:
    publisher = DiscoveryPublisher(DETAIL)
    other = DETAIL["identity"] | {"serial": "SN-OTHER"}
    with pytest.raises(IdentityError):
        publisher.update_identity(other)
    with pytest.raises(IdentityError):
        follow_events(publisher, [("device", {"identity": other})])


def api_with(details: list[dict]) -> httpx.MockTransport:
    """Each device answer in turn (the last one repeats); an empty stream after a snapshot."""
    snapshot = json.dumps({"points": {"label.a": point("label.a", 1)}})

    def answer(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/events"):

            async def body():
                yield f"event: snapshot\nid: 1\ndata: {snapshot}\n\n".encode()
                await asyncio.sleep(60)

            return httpx.Response(200, content=body())
        detail = details.pop(0) if len(details) > 1 else details[0]
        return httpx.Response(200, json=detail)

    return httpx.MockTransport(answer)


def test_reconnect_reads_the_device_answer_again(tmp_path: Path) -> None:
    broker = Broker()
    transport = api_with([DETAIL, DETAIL | {"identity": V2}])

    async def run() -> None:
        task = asyncio.create_task(mqtt.run(args(tmp_path), broker, transport))
        await broker.online(1)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(run())
    configs = [json.loads(v) for k, v in broker.retained.items() if k.endswith("/config")]
    assert configs and {c["device"]["sw_version"] for c in configs} == {"2.0.0"}


def test_reconnect_to_another_serial_marks_offline_and_stops(tmp_path: Path) -> None:
    broker = Broker()
    other = DETAIL | {"identity": DETAIL["identity"] | {"serial": "SN-OTHER"}}
    transport = api_with([DETAIL, other])

    async def run() -> None:
        await asyncio.wait_for(mqtt.run(args(tmp_path), broker, transport), 2)

    with pytest.raises(IdentityError):
        asyncio.run(run())
    assert broker.retained[AVAILABILITY] == "offline"
    assert not any(k.endswith("/config") for k in broker.retained)
