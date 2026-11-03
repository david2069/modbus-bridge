"""Home Assistant MQTT Discovery messages, built from the REST API's JSON (design D8).

Everything here is pure: it turns the API's device detail and points into MQTT
messages. The network side is in ``mqtt.py``.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import Any

DISCOVERY_PREFIX = "homeassistant"
DEFAULT_PREFIX = "modbus_bridge"
ONLINE = "online"
OFFLINE = "offline"

#: SunSpec unit spelling to Home Assistant's. Units not listed are passed on as they are.
HA_UNITS: dict[str, str] = {
    "W": "W",
    "Wh": "Wh",
    "WH": "Wh",
    "VA": "VA",
    "Var": "var",
    "VAr": "var",
    "V": "V",
    "A": "A",
    "Ah": "Ah",
    "AH": "Ah",
    "Hz": "Hz",
    "Pct": "%",
    "%": "%",
    "C": "°C",
    "Secs": "s",
}

#: Home Assistant device class for each HA unit.
HA_DEVICE_CLASSES: dict[str, str] = {
    "W": "power",
    "VA": "apparent_power",
    "var": "reactive_power",
    "V": "voltage",
    "A": "current",
    "Hz": "frequency",
    "°C": "temperature",
}

#: Models whose entities are enabled by default: measurements of inverters,
#: meters, storage, batteries and DERs. Entities of other models (settings,
#: curves) are created but disabled by default.
ENABLED_BY_DEFAULT_MODELS = frozenset(
    {101, 102, 103, 111, 112, 113, 124, 160, 201, 202, 203, 204}
    | {211, 212, 213, 214, 502, 701, 713, 714}
)

#: A Wh point whose name matches this counts energy over the device's life.
_LIFETIME_ENERGY = re.compile(r"^Tot|WhInj|WhAbs|WhIn$|WhOut$")


def slug(text: str) -> str:
    """``705.Crv[1].Pt[2].V`` gives ``m705_crv1_pt2_v``."""
    out = re.sub(r"[^0-9a-z]+", "_", text.lower()).strip("_")
    return f"m{out}" if out[:1].isdigit() else out


def model_id(key: str) -> int:
    return int(re.split(r"[.#]", key, maxsplit=1)[0])


def state_text(value: Any) -> str | None:
    """A point's JSON value as HA state text. ``None`` means unavailable."""
    if value is None:
        return None
    if isinstance(value, dict) and "names" in value:
        return ", ".join(value["names"]) or "none"
    if isinstance(value, dict) and "name" in value:
        if value["name"] == "UNKNOWN":
            return f"UNKNOWN ({value['value']})"
        return str(value["name"])
    if isinstance(value, bool):
        return "1" if value else "0"
    return str(value)


def _is_numeric(point: Mapping[str, Any]) -> bool:
    value = point.get("value")
    if isinstance(value, dict):
        return False
    sunspec_type = point.get("type") or ""
    return sunspec_type.startswith(("int", "uint", "acc", "float", "sunssf"))


def sensor_classes(point: Mapping[str, Any]) -> dict[str, str]:
    """Unit, device class and state class for one point, as discovery fields."""
    if not _is_numeric(point):
        return {}
    fields: dict[str, str] = {}
    units = point.get("units")
    ha_unit = HA_UNITS.get(units, units) if units else None
    if ha_unit:
        fields["unit_of_measurement"] = ha_unit
    name = point.get("name", "")
    sunspec_type = point.get("type") or ""
    if ha_unit == "Wh":
        if sunspec_type.startswith("acc") or _LIFETIME_ENERGY.search(name):
            fields["device_class"] = "energy"
            fields["state_class"] = "total_increasing"
            return fields
        fields["device_class"] = "energy_storage"
    elif ha_unit == "%" and name == "SoC":
        fields["device_class"] = "battery"
    elif ha_unit in HA_DEVICE_CLASSES:
        fields["device_class"] = HA_DEVICE_CLASSES[ha_unit]
    fields["state_class"] = "measurement"
    return fields


class IdentityError(ValueError):
    """The device has no Model 1 serial, so it cannot be given a stable identity."""


@dataclass(frozen=True)
class Message:
    topic: str
    payload: str
    retain: bool = True


class DiscoveryPublisher:
    """Build the MQTT messages for one device from the API's JSON."""

    def __init__(self, detail: Mapping[str, Any], prefix: str = DEFAULT_PREFIX) -> None:
        identity = detail.get("identity") or {}
        serial = identity.get("serial")
        if not serial:
            raise IdentityError(
                f"Device {detail.get('id')!r} has no Model 1 serial (SN); "
                "it cannot be given a stable Home Assistant identity"
            )
        self.prefix = prefix
        self.device_id = slug(serial)
        self.base = f"{prefix}/{self.device_id}"
        self.availability_topic = f"{self.base}/availability"
        maker = identity.get("manufacturer") or "SunSpec"
        model = identity.get("model") or "device"
        self.device = {
            "identifiers": [f"{prefix}_{self.device_id}"],
            "name": f"{maker} {model} {serial[-8:]}",
            "manufacturer": maker,
            "model": model,
            "serial_number": serial,
            **({"sw_version": identity["version"]} if identity.get("version") else {}),
        }

    def _topics(self, key: str) -> tuple[str, str, str, str]:
        point_slug = slug(key)
        unique_id = f"{self.prefix}_{self.device_id}_{point_slug}"
        return (
            unique_id,
            f"{DISCOVERY_PREFIX}/sensor/{unique_id}/config",
            f"{self.base}/{point_slug}/state",
            f"{self.base}/{point_slug}/available",
        )

    def discovery(self, point: Mapping[str, Any]) -> Message:
        key = point["key"]
        unique_id, config_topic, state_topic, available_topic = self._topics(key)
        label = point.get("label") or point["name"]
        path = key.split(".", 1)[1]
        name = label if path == point["name"] else f"{label} ({path})"
        payload: dict[str, Any] = {
            "unique_id": unique_id,
            "name": name,
            "state_topic": state_topic,
            "availability": [
                {"topic": self.availability_topic},
                {"topic": available_topic},
            ],
            "availability_mode": "all",
            "device": self.device,
            "enabled_by_default": model_id(key) in ENABLED_BY_DEFAULT_MODELS,
            **sensor_classes(point),
        }
        if model_id(key) == 1:
            payload["entity_category"] = "diagnostic"
        return Message(config_topic, json.dumps(payload, ensure_ascii=False))

    def state(self, point: Mapping[str, Any]) -> list[Message]:
        """The availability and, if available, the value of one point."""
        _, _, state_topic, available_topic = self._topics(point["key"])
        text = state_text(point.get("value"))
        if text is None:
            return [Message(available_topic, OFFLINE)]
        return [Message(state_topic, text), Message(available_topic, ONLINE)]

    def snapshot(self, points: Mapping[str, Mapping[str, Any]]) -> Iterator[Message]:
        """Everything for a full snapshot: discovery, states, then device online."""
        for point in points.values():
            yield self.discovery(point)
        for point in points.values():
            yield from self.state(point)
        yield Message(self.availability_topic, ONLINE)

    def offline(self) -> Message:
        return Message(self.availability_topic, OFFLINE)


@dataclass(frozen=True)
class Event:
    event: str
    id: str | None
    data: str


class SseParser:
    """Parse server-sent event lines, given one at a time without line endings."""

    def __init__(self) -> None:
        self._reset()

    def _reset(self) -> None:
        self._event = "message"
        self._id: str | None = None
        self._data: list[str] = []

    def feed(self, line: str) -> Event | None:
        """Return an event when ``line`` completes one, else ``None``."""
        if line == "":
            done = Event(self._event, self._id, "\n".join(self._data)) if self._data else None
            self._reset()
            return done
        if line.startswith(":"):
            return None  # a comment, e.g. keep-alive
        field, _, value = line.partition(":")
        value = value.removeprefix(" ")
        if field == "event":
            self._event = value
        elif field == "id":
            self._id = value
        elif field == "data":
            self._data.append(value)
        return None
