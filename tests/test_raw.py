"""Tests for raw register readings in quirk sets. All registers and values are made up."""

import asyncio
import json
import math
import struct
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from modbus_connection import IllegalDataAddressError
from modbus_connection.mock import MockModbusUnit
from test_api import AUTH, TOKEN, load_device
from test_quirks import active, q, quirk_set

from modbus_bridge.api import create_app
from modbus_bridge.quirks import QuirkError, QuirkSet, load_sets
from modbus_bridge.raw import RawReading, parse_reading, plan_blocks, read_raw
from modbus_bridge.service import DeviceService


def r(rid: str, address: int, rtype: str = "uint16", name: str | None = None, **more) -> dict:
    return {"id": rid, "name": name or rid, "reason": "test", "address": address, "type": rtype,
            **more}  # fmt: skip


def reading(data: dict, layer: str = "vendor") -> RawReading:
    return parse_reading(data, layer, "test-set", "made up")


def words(fmt: str, value) -> list[int]:
    raw = struct.pack(fmt, value)
    return list(struct.unpack(f">{len(raw) // 2}H", raw))


@pytest.mark.parametrize(
    ("rtype", "fmt", "value"),
    [
        ("uint16", ">H", 65000),
        ("int16", ">h", -5),
        ("uint32", ">I", 4_000_000_000),
        ("int32", ">i", -123_456),
        ("uint64", ">Q", 2**60),
        ("int64", ">q", -(2**40)),
        ("float32", ">f", 1.5),
    ],
)
@pytest.mark.parametrize("order", ["big", "little"])
def test_decode_each_type_and_word_order(rtype: str, fmt: str, value, order: str) -> None:
    regs = words(fmt, value)
    if order == "little":
        regs = regs[::-1]
    assert reading(r("x", 0, rtype, word_order=order)).decode(regs) == value


def test_scale_invert_and_unavailable() -> None:
    assert reading(r("x", 0, scale=0.1)).decode([1234]) == 123.4
    assert reading(r("x", 0, "int16", invert=True)).decode(words(">h", -250)) == 250
    spare = reading(r("x", 0, unavailable=[65535]))
    assert spare.decode([65535]) is None
    assert spare.decode([7]) == 7


def test_nan_is_no_value() -> None:
    assert reading(r("x", 0, "float32")).decode(words(">f", math.nan)) is None


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"colour": "red"}, "unknown field"),
        ({"type": "string"}, "type must be"),
        ({"address": -1}, "address"),
        ({"address": 65535, "type": "uint32"}, "past 65535"),
        ({"table": "coil"}, "table"),
        ({"word_order": "middle"}, "word_order"),
        ({"scale": 0}, "scale"),
        ({"invert": 1}, "invert"),
        ({"name": "Bad Name"}, "name"),
        ({"unavailable": "65535"}, "unavailable"),
    ],
)
def test_bad_readings_refused(change: dict, message: str) -> None:
    with pytest.raises(QuirkError, match=message):
        QuirkSet.from_json(quirk_set(quirks=[]) | {"readings": [r("x", 0) | change]})


def test_same_name_twice_in_one_set_refused() -> None:
    with pytest.raises(QuirkError, match="used twice"):
        QuirkSet.from_json(quirk_set() | {"readings": [r("a", 0, name="n"), r("b", 1, name="n")]})


def test_blocks_join_touching_registers_only() -> None:
    readings = [
        reading(r("a", 1000)),
        reading(r("b", 1001, "int32")),
        reading(r("c", 1003)),
        reading(r("d", 1010)),
        reading(r("e", 1000, table="input")),
    ]
    blocks = [(b.table, b.address, b.count) for b in plan_blocks(readings)]
    assert blocks == [("holding", 1000, 4), ("holding", 1010, 1), ("input", 1000, 1)]


def test_blocks_stop_at_125_registers() -> None:
    readings = [reading(r(f"x{i}", i, "uint64")) for i in range(0, 128, 4)]
    assert [b.count for b in plan_blocks(readings)] == [124, 4]


def test_failed_block_is_read_reading_by_reading(mock_modbus_unit: MockModbusUnit) -> None:
    mock_modbus_unit.holding[1001] = [2, 7]
    mock_modbus_unit.fail_read(1000, IllegalDataAddressError(2))  # the block starts here too
    readings = [reading(r("gap", 1000)), reading(r("a", 1001)), reading(r("b", 1002))]
    results = asyncio.run(read_raw(mock_modbus_unit, readings))
    assert (results["a"].value, results["b"].value) == (2, 7)
    assert results["gap"].value is None
    assert "1000" in results["gap"].error


def test_input_table(mock_modbus_unit: MockModbusUnit) -> None:
    mock_modbus_unit.input[30] = [9]
    results = asyncio.run(read_raw(mock_modbus_unit, [reading(r("i", 30, table="input"))]))
    assert results["i"].value == 9


def raw_set(layer: str, *readings: dict, set_id: str | None = None) -> dict:
    match = {
        "vendor": {"manufacturer": "ExampleMaker"},
        "model": {"manufacturer": "ExampleMaker", "model": ["ExampleModel"]},
    }[layer]
    return quirk_set(layer, match, set_id=set_id) | {"readings": list(readings)}


def test_higher_layer_replaces_by_name_and_off_falls_back() -> None:
    vendor = raw_set("vendor", r("v-mode", 1000, name="mode"))
    model = raw_set("model", r("m-mode", 2000, name="mode"))
    found = active(vendor, model)
    assert [x.id for x in found.readings] == ["m-mode"]
    states = {e["id"]: e["state"] for e in found.report()["readings"]}
    assert states == {"v-mode": "overridden", "m-mode": "active"}
    found = active(vendor, model, off=["m-mode"])
    assert [x.id for x in found.readings] == ["v-mode"]


def test_same_name_same_layer_in_two_sets_clashes() -> None:
    a = raw_set("vendor", r("a", 1000, name="mode"), set_id="a")
    b = raw_set("vendor", r("b", 2000, name="mode"), set_id="b")
    found = active(a, b)
    assert found.readings == []
    [point] = found.raw_states({})
    assert (point.key, point.value) == ("raw.mode", None)
    assert {e["id"]: e["state"] for e in found.report()["readings"]} == {
        "a": "failing",
        "b": "failing",
    }


def test_reading_ids_are_checked(tmp_path: Path) -> None:
    with pytest.raises(QuirkError, match="no-such"):
        active(raw_set("vendor", r("a", 1000)), off=["no-such"])
    (tmp_path / "a.json").write_text(
        json.dumps(raw_set("vendor", r("dup", 1000)) | {"quirks": [q("dup", "103.W", scale=2)]})
    )
    with pytest.raises(QuirkError, match="'dup' is used twice"):
        load_sets([tmp_path])


def test_point_quirk_on_raw_key() -> None:
    found = active(
        raw_set("vendor", r("p", 1000, units="W")) | {"quirks": [q("pq", "raw.p", label="Power")]}
    )
    [state] = found.raw_states({})
    out = found.apply(state)
    assert out.label == "Power"
    assert out.quirks == ("p", "pq")


def test_through_the_service_and_api(mock_modbus_unit: MockModbusUnit) -> None:
    load_device(mock_modbus_unit)
    mock_modbus_unit.holding[1000] = [2, *words(">i", -1234)[::-1]]
    mock_modbus_unit.fail_read(1010, IllegalDataAddressError(2))
    sets = [
        QuirkSet.from_json(
            raw_set(
                "vendor",
                r("mode", 1000),
                r("batt_w", 1001, "int32", word_order="little", invert=True, units="W"),
                r("missing", 1010),
            )
        )
    ]
    service = DeviceService(
        "unit1", mock_modbus_unit, interval=60, reads=1, read_interval=0, quirk_sets=sets
    )
    asyncio.run(service.setup())
    client = TestClient(create_app({"unit1": service}, [TOKEN]))
    points = client.get("/api/v1/devices/unit1/points", headers=AUTH).json()["points"]
    assert points["raw.mode"]["value"] == 2
    assert points["raw.batt_w"]["value"] == 1234
    assert points["raw.batt_w"]["units"] == "W"
    assert points["raw.batt_w"]["type"] == "int32"
    assert points["raw.missing"]["available"] is False
    assert points["713.SoC"]["value"] == 87.5
    body = client.get("/api/v1/devices/unit1/quirks", headers=AUTH).json()
    entries = {e["id"]: e for e in body["readings"]}
    assert entries["mode"]["state"] == "active"
    assert entries["mode"]["address"] == 1000
    assert entries["missing"]["state"] == "failing"
    assert "1010" in entries["missing"]["error"]
