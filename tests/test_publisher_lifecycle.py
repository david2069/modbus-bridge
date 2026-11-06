"""Tests for the publisher's stop and broker reconnect (rule 8). All values are made up."""

import argparse
import asyncio
import json
import os
import signal
from pathlib import Path

import aiomqtt
import httpx
import pytest
from test_mqtt_publisher import DETAIL, point
from test_removed import FakeMqtt

from modbus_bridge import mqtt
from modbus_bridge.mqtt_publisher import DiscoveryPublisher

PUBLISHER = DiscoveryPublisher(DETAIL)
AVAILABILITY = PUBLISHER.availability_topic
SNAPSHOT = json.dumps({"points": {"label.a": point("label.a", 1)}})


class Broker:
    """Hands out fake clients sharing one retained store; can fail on demand."""

    def __init__(self, refuse: int = 0) -> None:
        self.retained: dict[str, str] = {}
        self.clients: list[FakeClient] = []
        self.refuse = refuse  # connections to refuse first
        self.onlines = 0  # times a client marked the device online
        self.changed = asyncio.Event()

    async def online(self, times: int) -> None:
        """Wait until the device has been marked online ``times`` times."""
        async with asyncio.timeout(2):
            while self.onlines < times:
                await self.changed.wait()
                self.changed.clear()

    def __call__(self, **kwargs) -> "FakeClient":
        client = FakeClient(self, kwargs["will"])
        self.clients.append(client)
        return client


class FakeClient(FakeMqtt):
    def __init__(self, broker: Broker, will: aiomqtt.Will) -> None:
        super().__init__()
        self.retained = broker.retained
        self.broker = broker
        self.will = will
        self.fail_publish = False

    async def __aenter__(self) -> "FakeClient":
        if self.broker.refuse:
            self.broker.refuse -= 1
            raise aiomqtt.MqttError("connection refused")
        return self

    async def __aexit__(self, *exc) -> None:
        return None

    async def publish(self, topic: str, payload: str, qos: int, retain: bool) -> None:
        if self.fail_publish:
            raise aiomqtt.MqttCodeError(4, "The client is not currently connected.")
        await super().publish(topic, payload, qos, retain)
        if topic == AVAILABILITY and payload == "online":
            self.broker.onlines += 1
            self.broker.changed.set()


def args(tmp_path: Path) -> argparse.Namespace:
    (tmp_path / "token").write_text("not-secret\n")
    return argparse.Namespace(
        api_url="http://api.invalid", token_file=tmp_path / "token", device_id="unit1",
        mqtt_host="192.0.2.20", mqtt_port=1883, prefix="modbus_bridge",
    )  # fmt: skip


def api() -> httpx.MockTransport:
    def answer(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/events"):
            # A stream that stays open after the snapshot, as the real one does.
            async def body():
                yield f"event: snapshot\nid: 1\ndata: {SNAPSHOT}\n\n".encode()
                await asyncio.sleep(60)

            return httpx.Response(200, content=body())
        return httpx.Response(200, json=DETAIL)

    return httpx.MockTransport(answer)


@pytest.fixture(autouse=True)
def fast_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mqtt, "RETRY_SECONDS", 0.05)


def test_cancel_marks_offline(tmp_path: Path) -> None:
    broker = Broker()

    async def run() -> None:
        task = asyncio.create_task(mqtt.run(args(tmp_path), broker, api()))
        await broker.online(1)
        task.cancel()  # what Ctrl-C and SIGTERM do
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(run())
    assert broker.retained[AVAILABILITY] == "offline"
    assert broker.clients[0].will.topic == AVAILABILITY


def test_stop_goes_ahead_when_offline_cannot_be_sent(tmp_path: Path) -> None:
    broker = Broker()

    async def run() -> None:
        task = asyncio.create_task(mqtt.run(args(tmp_path), broker, api()))
        await broker.online(1)
        broker.clients[0].fail_publish = True
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(task, 2)

    asyncio.run(run())
    assert broker.retained[AVAILABILITY] == "online"  # the broker's last will covers this


def test_lost_broker_reconnects_with_new_snapshot(tmp_path: Path) -> None:
    broker = Broker()

    def failing_api() -> httpx.MockTransport:
        calls = {"n": 0}

        def answer(request: httpx.Request) -> httpx.Response:
            if request.url.path.endswith("/events"):
                calls["n"] += 1
                first = calls["n"] == 1

                async def body():
                    yield f"event: snapshot\nid: 1\ndata: {SNAPSHOT}\n\n".encode()
                    if first:
                        broker.retained.clear()  # a restart without stored messages
                        broker.clients[0].fail_publish = True
                        change = json.dumps(point("label.a", 2))
                        yield f"event: change\nid: 2\ndata: {change}\n\n".encode()
                    await asyncio.sleep(60)

                return httpx.Response(200, content=body())
            return httpx.Response(200, json=DETAIL)

        return httpx.MockTransport(answer)

    async def drive() -> None:
        task = asyncio.create_task(mqtt.run(args(tmp_path), broker, failing_api()))
        await broker.online(2)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(drive())
    assert len(broker.clients) == 2
    configs = [t for t, _ in broker.clients[1].sent if t.endswith("/config")]
    assert configs == [PUBLISHER.discovery(point("label.a", 1)).topic]


def test_broker_not_reachable_at_start_is_retried(tmp_path: Path) -> None:
    broker = Broker(refuse=2)

    async def run() -> None:
        task = asyncio.create_task(mqtt.run(args(tmp_path), broker, api()))
        await broker.online(1)
        assert len(broker.clients) == 3
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(run())
    assert broker.retained[AVAILABILITY] == "offline"


def test_sigterm_is_an_orderly_stop() -> None:
    stopped = []

    async def work() -> None:
        try:
            await asyncio.sleep(10)
        finally:
            stopped.append(True)

    async def run() -> None:
        loop = asyncio.get_running_loop()
        loop.call_later(0.05, os.kill, os.getpid(), signal.SIGTERM)
        await asyncio.wait_for(mqtt.until_stopped(work()), 2)

    asyncio.run(run())
    assert stopped == [True]
