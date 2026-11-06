"""Tests for unit, label and scale changes reaching HA, with warnings (design Q4).

All values are made up.
"""

import asyncio
import json
from pathlib import Path

import httpx
from modbus_connection.mock import MockModbusUnit
from test_api import AUTH
from test_mqtt_publisher import DETAIL, point
from test_quirks import q
from test_removed import FakeMqtt
from test_user_quirks import BASE, make, poll

from modbus_bridge.mqtt import follow
from modbus_bridge.mqtt_publisher import DiscoveryPublisher, sensor_classes


def save(client, item: dict) -> dict:
    answer = client.put(f"{BASE}/user-quirks/quirk/{item['id']}", json=item, headers=AUTH)
    assert answer.status_code == 200, answer.json()
    return answer.json()


def test_unit_or_label_only_change_is_reported(
    mock_modbus_unit: MockModbusUnit, tmp_path: Path
) -> None:
    service, client = make(mock_modbus_unit, tmp_path)
    assert asyncio.run(service.poll_once()) == []  # nothing changed
    save(client, q("u-unit", "713.SoC", units="percent", reason="r"))
    [change] = asyncio.run(service.poll_once())
    assert (change.key, change.units, change.value) == ("713.SoC", "percent", 87.5)
    save(client, q("u-name", "713.SoC", label="Charge", reason="r"))
    [change] = asyncio.run(service.poll_once())
    assert change.label == "Charge"
    assert asyncio.run(service.poll_once()) == []


def test_publisher_resends_config_only_when_it_changes() -> None:
    publisher = DiscoveryPublisher(DETAIL)
    w = point("label.load", 2056, units="W", sunspec_type="rule")
    events = [
        ("snapshot", {"points": {"label.load": w}}),
        ("change", w | {"value": 2060}),  # value only: no config
        ("change", w | {"value": 2.06, "units": "kW"}),  # new unit: config
        ("change", w | {"value": None, "units": "kWh"}),  # unavailable: config kept
        ("change", w | {"value": 2.07, "units": "kW", "label": "Load"}),  # new name: config
    ]
    body = "".join(f"event: {e}\nid: {i}\ndata: {json.dumps(d)}\n\n" for i, (e, d) in
                   enumerate(events))  # fmt: skip
    transport = httpx.MockTransport(lambda request: httpx.Response(200, text=body))
    mqtt = FakeMqtt()

    async def run() -> None:
        async with httpx.AsyncClient(transport=transport) as http:
            await follow(mqtt, http, publisher, "http://api.invalid", "unit1")

    asyncio.run(run())
    topic = publisher.discovery(w).topic
    configs = [json.loads(p) for t, p in mqtt.sent if t == topic]
    assert [c.get("unit_of_measurement") for c in configs] == ["W", "kW", "kW"]
    assert configs[1]["device_class"] == "power"
    assert configs[2]["name"].startswith("Load")


def test_kw_and_kwh_classes() -> None:
    kw = sensor_classes(point("label.load", 2.0, units="kW", sunspec_type="rule"))
    assert kw == {"unit_of_measurement": "kW", "device_class": "power",
                  "state_class": "measurement"}  # fmt: skip
    kwh = point("label.e", 1.5, units="kWh", sunspec_type="rule") | {"total": True}
    assert sensor_classes(kwh)["device_class"] == "energy"
    assert sensor_classes(kwh)["state_class"] == "total_increasing"


def test_check_and_save_warn_for_unit_and_scale(
    mock_modbus_unit: MockModbusUnit, tmp_path: Path
) -> None:
    _, client = make(mock_modbus_unit, tmp_path)
    body = {"kind": "quirk", "item": q("u-a", "713.SoC", scale=0.01, units="fraction",
                                        reason="r")}  # fmt: skip
    [warning] = client.post(f"{BASE}/user-quirks/check", json=body, headers=AUTH).json()["warnings"]
    assert warning.startswith("713.SoC: unit Pct → fraction.")
    assert "statistics" in warning
    [warning] = save(client, q("u-b", "713.WHRtg", scale=2, reason="r"))["warnings"]
    assert warning.startswith("713.WHRtg: value 13500 → 27000 with the same unit WH")
    assert save(client, q("u-c", "713.WHAvail", label="Left", reason="r"))["warnings"] == []


def test_remove_and_off_warn_when_unit_goes_back(
    mock_modbus_unit: MockModbusUnit, tmp_path: Path
) -> None:
    service, client = make(mock_modbus_unit, tmp_path)
    save(client, q("u-a", "713.SoC", units="fraction", reason="r"))
    poll(service)
    [warning] = client.put(f"{BASE}/quirks/u-a/off", headers=AUTH).json()["warnings"]
    assert warning.startswith("713.SoC: unit fraction → Pct.")
    poll(service)
    [warning] = client.delete(f"{BASE}/quirks/u-a/off", headers=AUTH).json()["warnings"]
    assert warning.startswith("713.SoC: unit Pct → fraction.")
    poll(service)
    [warning] = client.delete(f"{BASE}/user-quirks/quirk/u-a", headers=AUTH).json()["warnings"]
    assert warning.startswith("713.SoC: unit fraction → Pct.")
