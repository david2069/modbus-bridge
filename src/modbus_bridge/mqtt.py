"""Run the MQTT Discovery publisher: a client of the REST API (design D7, D8, D9).

Usage:
    python -m modbus_bridge.mqtt --api-url http://127.0.0.1:8080 --token-file PATH
        --device-id unit1 --mqtt-host 192.0.2.20 [--mqtt-port 1883] [--prefix modbus_bridge]

It reads the device from the API, then follows the API's event stream: a
snapshot publishes every entity and state, each change publishes that
point's state, and each removal deletes that point's entity. If the stream
is lost, the device is marked offline in Home Assistant and the publisher
reconnects.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
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


async def _publish(client: aiomqtt.Client, messages: Any) -> int:
    count = 0
    for message in messages:
        assert isinstance(message, Message)
        await client.publish(message.topic, message.payload, qos=1, retain=message.retain)
        count += 1
    return count


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
                count = await _publish(client, publisher.snapshot(points))
                _LOGGER.info("Snapshot: %d points, %d messages", len(points), count)
            elif event.event == "change":
                messages = []
                # Without a value an enum point cannot be told from a number, so the
                # config of an unavailable point that is already known is left as it is.
                if data["key"] not in sent or data.get("value") is not None:
                    config = publisher.discovery(data)
                    if sent.get(data["key"]) != config.payload:
                        messages.append(config)
                        sent[data["key"]] = config.payload
                await _publish(client, [*messages, *publisher.state(data)])
            elif event.event == "removed":
                sent.pop(data["key"], None)
                await _publish(client, publisher.remove(data["key"]))
                _LOGGER.info("Removed %s from Home Assistant", data["key"])


async def run(args: argparse.Namespace) -> None:
    token = args.token_file.read_text().strip()
    headers = {"Authorization": f"Bearer {token}"}
    timeout = httpx.Timeout(10.0, read=READ_TIMEOUT)
    async with httpx.AsyncClient(headers=headers, timeout=timeout) as http:
        while True:
            try:
                detail = await fetch_detail(http, args.api_url, args.device_id)
                break
            except httpx.HTTPError as err:
                _LOGGER.warning("API not reachable (%s); retrying", err)
                await asyncio.sleep(RETRY_SECONDS)
        publisher = DiscoveryPublisher(detail, prefix=args.prefix)
        will = aiomqtt.Will(publisher.availability_topic, OFFLINE, qos=1, retain=True)
        async with aiomqtt.Client(
            hostname=args.mqtt_host,
            port=args.mqtt_port,
            identifier=f"{args.prefix}_{publisher.device_id}",
            will=will,
        ) as client:
            _LOGGER.info("Publishing %s to MQTT under %s", args.device_id, publisher.base)
            while True:
                try:
                    await follow(client, http, publisher, args.api_url, args.device_id)
                    _LOGGER.warning("Event stream ended")
                except httpx.HTTPError as err:
                    _LOGGER.warning("Event stream lost: %s", err)
                await _publish(client, [publisher.offline()])
                _LOGGER.info("Device marked offline; reconnecting in %.0f s", RETRY_SECONDS)
                await asyncio.sleep(RETRY_SECONDS)


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
        asyncio.run(run(args))
    except IdentityError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
