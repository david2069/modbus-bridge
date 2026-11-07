"""Run the MQTT Discovery publisher: a client of the REST API (design D7, D8, D9).

Usage:
    python -m modbus_bridge.mqtt --api-url http://127.0.0.1:8080 --token-file PATH
        --device-id unit1 --mqtt-host 192.0.2.20 [--mqtt-port 1883] [--prefix modbus_bridge]

It reads the device from the API, then follows the API's event stream: a
snapshot publishes every entity and state, each change publishes that
point's state, and each removal deletes that point's entity. After each
snapshot it also deletes this device's entities that the broker still keeps
but the snapshot no longer has (from changes made while it was not running).
A ``device`` event (new firmware or options) sends every entity config again
with the new device info. The device answer is read again on each reconnect
to the API. If the device reports another serial, the publisher stops.

Every stop marks the device offline in Home Assistant: Ctrl-C and SIGTERM
publish ``offline`` before disconnecting, and the broker's last will covers
a crash. A lost broker is retried like a lost API, from a fresh snapshot. If the stream
is lost, the device is marked offline in Home Assistant and the publisher
reconnects.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import signal
import sys
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import aiomqtt
import httpx

from .mqtt_publisher import (
    OFFLINE,
    DiscoveryPublisher,
    IdentityError,
    Message,
    SseParser,
)

_LOGGER = logging.getLogger(__name__)
RETRY_SECONDS = 5.0
#: The API sends a keep-alive every 15 s, so a silent stream for this long is dead.
READ_TIMEOUT = 45.0
#: Reading back retained configs ends after this long without a message...
RETAINED_QUIET = 1.0
#: ...or after this long in all.
RETAINED_LIMIT = 10.0


async def _publish(client: aiomqtt.Client, messages: Any) -> int:
    count = 0
    for message in messages:
        assert isinstance(message, Message)
        await client.publish(message.topic, message.payload, qos=1, retain=message.retain)
        count += 1
    return count


async def read_retained(
    client: aiomqtt.Client,
    topic_filter: str,
    quiet: float | None = None,
    limit: float | None = None,
) -> dict[str, str]:
    """The retained messages under ``topic_filter``, by topic."""
    quiet = RETAINED_QUIET if quiet is None else quiet
    limit = RETAINED_LIMIT if limit is None else limit
    found: dict[str, str] = {}
    await client.subscribe(topic_filter, qos=1)
    try:
        async with asyncio.timeout(limit):
            messages = aiter(client.messages)
            while True:
                try:
                    message = await asyncio.wait_for(anext(messages), quiet)
                except TimeoutError:
                    break
                payload = message.payload
                if message.retain and isinstance(payload, (bytes, bytearray)) and payload:
                    found[str(message.topic)] = payload.decode("utf-8", "replace")
    except TimeoutError:
        _LOGGER.warning("Read %d retained configs in %.0f s; there may be more", len(found), limit)
    finally:
        await client.unsubscribe(topic_filter)
    return found


async def remove_stale(
    client: aiomqtt.Client, publisher: DiscoveryPublisher, points: dict[str, Any]
) -> int:
    """Delete this device's retained entities that ``points`` no longer has."""
    retained = await read_retained(client, publisher.config_filter)
    stale = publisher.stale(retained, points)
    for unique_id, messages in stale:
        await _publish(client, messages)
        _LOGGER.info("Removed stale entity %s from Home Assistant", unique_id)
    return len(stale)


async def fetch_detail(http: httpx.AsyncClient, base: str, device_id: str) -> dict[str, Any]:
    response = await http.get(f"{base}/api/v1/devices/{device_id}")
    response.raise_for_status()
    return response.json()


async def follow(
    client: aiomqtt.Client,
    http: httpx.AsyncClient,
    publisher: DiscoveryPublisher,
    base: str,
    device_id: str,
) -> None:
    """Publish from the event stream until it ends or fails."""
    sent: dict[str, str] = {}
    """The discovery config last sent for each point, to send it again when it changes."""
    configured: dict[str, dict[str, Any]] = {}
    """The point each sent config was built from, to build it again for new device info."""
    parser = SseParser()
    url = f"{base}/api/v1/devices/{device_id}/events"
    async with http.stream("GET", url) as response:
        response.raise_for_status()
        async for line in response.aiter_lines():
            event = parser.feed(line)
            if event is None:
                continue
            data = json.loads(event.data)
            if event.event == "snapshot":
                points = data["points"]
                sent = {key: publisher.discovery(p).payload for key, p in points.items()}
                configured = dict(points)
                count = await _publish(client, publisher.snapshot(points))
                _LOGGER.info("Snapshot: %d points, %d messages", len(points), count)
                await remove_stale(client, publisher, points)
            elif event.event == "change":
                messages = []
                # Without a value an enum point cannot be told from a number, so the
                # config of an unavailable point that is already known is left as it is.
                if data["key"] not in sent or data.get("value") is not None:
                    config = publisher.discovery(data)
                    if sent.get(data["key"]) != config.payload:
                        messages.append(config)
                        sent[data["key"]] = config.payload
                        configured[data["key"]] = data
                await _publish(client, [*messages, *publisher.state(data)])
            elif event.event == "removed":
                sent.pop(data["key"], None)
                configured.pop(data["key"], None)
                await _publish(client, publisher.remove(data["key"]))
                _LOGGER.info("Removed %s from Home Assistant", data["key"])
            elif event.event == "device":
                if publisher.update_identity(data["identity"]):
                    configs = [publisher.discovery(p) for p in configured.values()]
                    sent = {key: c.payload for key, c in zip(configured, configs, strict=True)}
                    await _publish(client, configs)
                    _LOGGER.info("Device info changed (firmware %s); %d configs sent again",
                                 data["identity"].get("version"), len(configs))  # fmt: skip


async def mark_offline(client: aiomqtt.Client, publisher: DiscoveryPublisher) -> None:
    """Publish the device offline; if the broker is gone, its last will does it."""
    try:
        async with asyncio.timeout(RETRY_SECONDS):
            await _publish(client, [publisher.offline()])
        _LOGGER.info("Device marked offline")
    except (aiomqtt.MqttError, TimeoutError) as err:
        _LOGGER.warning("Could not mark the device offline (%s); the last will covers it", err)


async def _follow_forever(
    client: aiomqtt.Client, http: httpx.AsyncClient, publisher: DiscoveryPublisher, args: Any
) -> None:
    while True:
        try:
            # The device may have changed while the stream was down.
            detail = await fetch_detail(http, args.api_url, args.device_id)
            if publisher.update_identity(detail.get("identity") or {}):
                _LOGGER.info("Device info changed (firmware %s)",
                             (detail.get("identity") or {}).get("version"))  # fmt: skip
            await follow(client, http, publisher, args.api_url, args.device_id)
            _LOGGER.warning("Event stream ended")
        except httpx.HTTPError as err:
            _LOGGER.warning("Event stream lost: %s", err)
        await _publish(client, [publisher.offline()])
        _LOGGER.info("Device marked offline; reconnecting in %.0f s", RETRY_SECONDS)
        await asyncio.sleep(RETRY_SECONDS)


async def run(
    args: argparse.Namespace,
    connect: Callable[..., Any] = aiomqtt.Client,
    transport: httpx.AsyncBaseTransport | None = None,
) -> None:
    """Publish until cancelled. ``connect`` and ``transport`` are for tests."""
    token = args.token_file.read_text().strip()
    headers = {"Authorization": f"Bearer {token}"}
    timeout = httpx.Timeout(10.0, read=READ_TIMEOUT)
    async with httpx.AsyncClient(headers=headers, timeout=timeout, transport=transport) as http:
        while True:
            try:
                detail = await fetch_detail(http, args.api_url, args.device_id)
                break
            except httpx.HTTPError as err:
                _LOGGER.warning("API not reachable (%s); retrying", err)
                await asyncio.sleep(RETRY_SECONDS)
        publisher = DiscoveryPublisher(detail, prefix=args.prefix)
        will = aiomqtt.Will(publisher.availability_topic, OFFLINE, qos=1, retain=True)
        while True:
            try:
                async with connect(
                    hostname=args.mqtt_host,
                    port=args.mqtt_port,
                    identifier=f"{args.prefix}_{publisher.device_id}",
                    will=will,
                ) as client:
                    _LOGGER.info("Publishing %s to MQTT under %s", args.device_id, publisher.base)
                    try:
                        await _follow_forever(client, http, publisher, args)
                    finally:
                        # Also on Ctrl-C and SIGTERM: a clean disconnect sends no last will.
                        await mark_offline(client, publisher)
            except aiomqtt.MqttError as err:
                _LOGGER.warning("MQTT broker lost or not reachable (%s); retrying in %.0f s",
                                err, RETRY_SECONDS)  # fmt: skip
                await asyncio.sleep(RETRY_SECONDS)


async def until_stopped(work: Awaitable[None]) -> None:
    """Run ``work``; SIGTERM stops it in the same orderly way as Ctrl-C."""
    task = asyncio.ensure_future(work)
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGTERM, task.cancel)
    try:
        await task
    except asyncio.CancelledError:
        if not task.cancelled():
            raise
        _LOGGER.info("Stopped")
    finally:
        loop.remove_signal_handler(signal.SIGTERM)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--token-file", type=Path, required=True)
    parser.add_argument("--device-id", required=True)
    parser.add_argument("--mqtt-host", required=True)
    parser.add_argument("--mqtt-port", type=int, default=1883)
    parser.add_argument("--prefix", default="modbus_bridge")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    try:
        asyncio.run(until_stopped(run(args)))
    except IdentityError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
