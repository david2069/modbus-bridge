"""Tests for removing stale HA entities after a snapshot (rule 8). All values are made up."""

import asyncio
import json

import httpx
from test_mqtt_publisher import DETAIL, point
from test_removed import FakeMqtt

from modbus_bridge.mqtt import follow, read_retained
from modbus_bridge.mqtt_publisher import DiscoveryPublisher

PUBLISHER = DiscoveryPublisher(DETAIL)
LIVE = point("label.live", 1)
GONE = point("label.gone", 2)


def retained_for(*points: dict) -> dict[str, str]:
    """What the broker keeps after publishing ``points``."""
    retained = {}
    for p in points:
        for message in [PUBLISHER.discovery(p), *PUBLISHER.state(p)]:
            retained[message.topic] = message.payload
    return retained


def other_device_config() -> tuple[str, str]:
    """A device whose serial makes its topics start like ours."""
    other = DiscoveryPublisher(DETAIL | {"identity": DETAIL["identity"] | {
        "serial": DETAIL["identity"]["serial"] + "-x"}})  # fmt: skip
    config = other.discovery(point("label.gone", 2))
    assert config.topic.startswith(PUBLISHER.discovery(GONE).topic.rsplit("_label", 1)[0])
    return config.topic, config.payload


def test_stale_config_gives_three_empty_messages() -> None:
    gone_topics = {m.topic for m in [PUBLISHER.discovery(GONE), *PUBLISHER.state(GONE)]}
    [(unique_id, messages)] = PUBLISHER.stale(retained_for(LIVE, GONE), {"label.live": LIVE})
    assert unique_id.endswith("label_gone")
    assert {m.topic for m in messages} == gone_topics
    assert all(m.payload == "" and m.retain for m in messages)
    assert PUBLISHER.availability_topic not in gone_topics


def test_others_and_junk_are_kept() -> None:
    topic, payload = other_device_config()
    retained = retained_for(LIVE) | {
        topic: payload,
        "homeassistant/sensor/junk/config": "not json",
        "homeassistant/sensor/nodevice/config": json.dumps({"unique_id": "x"}),
    }
    assert PUBLISHER.stale(retained, {"label.live": LIVE}) == []


def test_read_retained_stops_when_quiet_and_unsubscribes() -> None:
    mqtt = FakeMqtt(retained_for(LIVE, GONE))

    async def run() -> dict[str, str]:
        return await asyncio.wait_for(read_retained(mqtt, PUBLISHER.config_filter), 2)

    found = asyncio.run(run())
    assert set(found) == {PUBLISHER.discovery(LIVE).topic, PUBLISHER.discovery(GONE).topic}
    assert mqtt.subscribed == []


def test_snapshot_removes_stale_entities() -> None:
    other_topic, other_payload = other_device_config()
    mqtt = FakeMqtt(retained_for(LIVE, GONE) | {other_topic: other_payload})
    body = f"event: snapshot\nid: 1\ndata: {json.dumps({'points': {'label.live': LIVE}})}\n\n"
    transport = httpx.MockTransport(lambda request: httpx.Response(200, text=body))

    async def run() -> None:
        async with httpx.AsyncClient(transport=transport) as http:
            await follow(mqtt, http, PUBLISHER, "http://api.invalid", "unit1")

    asyncio.run(run())
    assert PUBLISHER.discovery(GONE).topic not in mqtt.retained
    assert all(m.topic not in mqtt.retained for m in PUBLISHER.state(GONE))
    assert PUBLISHER.discovery(LIVE).topic in mqtt.retained
    assert mqtt.retained[other_topic] == other_payload
    assert mqtt.retained[PUBLISHER.availability_topic] == "online"
