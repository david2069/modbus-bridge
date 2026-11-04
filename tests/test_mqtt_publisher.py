"""Tests for building MQTT Discovery messages. All values are made up."""

import json

import pytest

from modbus_bridge.mqtt_publisher import (
    DiscoveryPublisher,
    IdentityError,
    SseParser,
    sensor_classes,
    slug,
    state_text,
)

DETAIL = {
    "id": "unit1",
    "identity": {
        "manufacturer": "ExampleMaker",
        "model": "ExampleModel",
        "version": "1.0.0",
        "serial": "SN-PLACEHOLDER-0001",
    },
}


def point(key: str, value, units=None, sunspec_type="uint16", label=None) -> dict:
    return {
        "key": key,
        "name": key.rsplit(".", 1)[-1],
        "label": label,
        "units": units,
        "type": sunspec_type,
        "writable": False,
        "value": value,
        "available": value is not None,
    }


def test_slug() -> None:
    assert slug("713.SoC") == "m713_soc"
    assert slug("705.Crv[1].Pt[2].V") == "m705_crv_1_pt_2_v"
    assert slug("701#2.W") == "m701_2_w"
    assert slug("SN-PLACEHOLDER-0001") == "sn_placeholder_0001"


@pytest.mark.parametrize(
    ("p", "expected"),
    [
        (point("701.W", 5.0, "W", "int16"), {"unit_of_measurement": "W", "device_class": "power"}),
        (point("713.SoC", 40.0, "Pct"), {"unit_of_measurement": "%", "device_class": "battery"}),
        (point("701.Var", 1.0, "Var", "int16"), {"device_class": "reactive_power"}),
        (
            point("701.TotWhInj", 9.0, "Wh", "uint64"),
            {"device_class": "energy", "state_class": "total_increasing"},
        ),
        (point("714.DCWhInj", 9.0, "Wh", "uint64"), {"state_class": "total_increasing"}),
        (point("713.WHRtg", 9.0, "WH"), {"device_class": "energy_storage"}),
        (point("x.E", 1.0, "Wh", "acc32"), {"state_class": "total_increasing"}),
    ],
)
def test_sensor_classes(p: dict, expected: dict) -> None:
    fields = sensor_classes(p)
    for key, value in expected.items():
        assert fields[key] == value
    if fields.get("device_class") != "energy":
        assert fields.get("state_class") in ("measurement", "total_increasing")


def test_energy_storage_is_measurement_not_total() -> None:
    assert sensor_classes(point("713.WHAvail", 9.0, "WH"))["state_class"] == "measurement"


def test_enum_and_string_have_no_unit() -> None:
    assert sensor_classes(point("701.InvSt", {"value": 3, "name": "RUNNING"}, None, "enum16")) == {}
    assert sensor_classes(point("1.Mn", "ExampleMaker", None, "string")) == {}


def test_state_text() -> None:
    assert state_text(None) is None
    assert state_text(40.0) == "40.0"
    assert state_text({"value": 3, "name": "RUNNING"}) == "RUNNING"
    assert state_text({"value": 0, "name": "UNKNOWN"}) == "UNKNOWN (0)"
    assert state_text({"value": 3, "names": ["A", "B"]}) == "A, B"
    assert state_text({"value": 0, "names": []}) == "none"


def test_refuses_without_serial() -> None:
    with pytest.raises(IdentityError, match="no Model 1 serial"):
        DiscoveryPublisher({"id": "unit1", "identity": {"serial": None}})


def test_discovery_payload() -> None:
    pub = DiscoveryPublisher(DETAIL)
    message = pub.discovery(point("713.SoC", 40.0, "Pct", label="State of Charge"))
    assert message.topic == (
        "homeassistant/sensor/modbus_bridge_sn_placeholder_0001_m713_soc/config"
    )
    assert message.retain
    payload = json.loads(message.payload)
    assert payload["unique_id"] == "modbus_bridge_sn_placeholder_0001_m713_soc"
    assert payload["name"] == "State of Charge"
    assert payload["state_topic"] == "modbus_bridge/sn_placeholder_0001/m713_soc/state"
    assert payload["availability_mode"] == "all"
    assert [a["topic"] for a in payload["availability"]] == [
        "modbus_bridge/sn_placeholder_0001/availability",
        "modbus_bridge/sn_placeholder_0001/m713_soc/available",
    ]
    assert payload["device"]["identifiers"] == ["modbus_bridge_sn_placeholder_0001"]
    assert payload["enabled_by_default"] is True


def test_curve_points_disabled_by_default_and_named_with_path() -> None:
    pub = DiscoveryPublisher(DETAIL)
    payload = json.loads(
        pub.discovery(point("705.Crv[1].Pt[2].V", 1.0, label="Voltage Point")).payload
    )
    assert payload["enabled_by_default"] is False
    assert payload["name"] == "Voltage Point (Crv[1].Pt[2].V)"


def test_unavailable_point_goes_offline_without_a_value() -> None:
    pub = DiscoveryPublisher(DETAIL)
    [message] = pub.state(point("713.SoH", None, "Pct"))
    assert message.topic.endswith("/m713_soh/available")
    assert message.payload == "offline"
    state, available = pub.state(point("713.SoC", 40.0, "Pct"))
    assert (state.payload, available.payload) == ("40.0", "online")


def test_sse_parser() -> None:
    parser = SseParser()
    lines = ["event: snapshot", "id: 3", 'data: {"a": 1}', "", ": keep-alive", "", "data: x", ""]
    events = [e for e in map(parser.feed, lines) if e is not None]
    assert [(e.event, e.id, e.data) for e in events] == [
        ("snapshot", "3", '{"a": 1}'),
        ("message", None, "x"),
    ]


def label(name: str, value, units=None, options=None, total=False) -> dict:
    out = point(f"label.{name}", value, units, "rule", label=name.replace("_", " ").capitalize())
    if options is not None:
        out["options"] = options
    if total:
        out["total"] = True
    return out


def test_raw_and_label_points() -> None:
    pub = DiscoveryPublisher(DETAIL)
    raw = json.loads(pub.discovery(point("raw.mode", 2)).payload)
    lab = json.loads(pub.discovery(label("load_power", 312, "W")).payload)
    assert raw["enabled_by_default"] is False
    assert lab["enabled_by_default"] is True
    assert "entity_category" not in raw and "entity_category" not in lab
    assert lab["name"] == "Load power"
    assert lab["unique_id"].endswith("_label_load_power")
    assert (lab["unit_of_measurement"], lab["device_class"], lab["state_class"]) == (
        "W",
        "power",
        "measurement",
    )


def test_enum_label() -> None:
    fields = sensor_classes(label("mode", "backup", options=["backup", "self_consumption"]))
    assert fields == {"device_class": "enum", "options": ["backup", "self_consumption"]}
    assert sensor_classes(label("fitted", 1, options=[0, 1]))["options"] == ["0", "1"]


def test_text_label_has_no_classes() -> None:
    assert sensor_classes(label("note", "hello")) == {}


def test_total_marks_lifetime_energy() -> None:
    assert sensor_classes(label("solar_energy", 10, "Wh", total=True)) == {
        "unit_of_measurement": "Wh",
        "device_class": "energy",
        "state_class": "total_increasing",
    }
    assert sensor_classes(point("raw.e", 10, "Wh", "uint32"))["device_class"] == "energy_storage"
    # The SunSpec name pattern applies to SunSpec points only.
    assert sensor_classes(point("raw.TotWhInj", 10, "Wh", "uint32"))["device_class"] == (
        "energy_storage"
    )
