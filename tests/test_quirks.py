"""Tests for quirk sets (design L2–L4). All quirks and devices are made up."""

import asyncio
import json
from enum import IntEnum
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from modbus_connection.mock import MockModbusUnit
from test_api import AUTH, TOKEN, load_device

from modbus_bridge.api import create_app
from modbus_bridge.poller import PointState
from modbus_bridge.quirks import ActiveQuirks, QuirkError, QuirkSet, load_sets, version_numbers
from modbus_bridge.service import DeviceService
from modbus_bridge.sunspec import DeviceIdentity

IDENT = DeviceIdentity("ExampleMaker", "ExampleModel", None, "V1R02B03", "SN-PLACEHOLDER", 1)


def quirk_set(layer: str = "vendor", match: dict | None = None, quirks=(), set_id=None) -> dict:
    return {
        "format": "modbus-bridge/quirk-set",
        "version": 1,
        "id": set_id or f"test-{layer}",
        "layer": layer,
        "match": match or {"manufacturer": "ExampleMaker"},
        "source": "made up for tests",
        "quirks": list(quirks),
    }


def q(qid: str, point: str, **changes) -> dict:
    return {"id": qid, "point": point, "reason": "test", **changes}


def state(key: str, value, units="W", label="Watts") -> PointState:
    return PointState(key, key.rsplit(".", 1)[-1], label, units, False, value, "int16")


def active(*sets: dict, off=(), identity=IDENT) -> ActiveQuirks:
    return ActiveQuirks([QuirkSet.from_json(s) for s in sets], identity, off)


def test_version_numbers() -> None:
    assert version_numbers("V12R02B60D00") == (12, 2, 60, 0)
    assert version_numbers("1.0.0") == (1, 0, 0)
    assert version_numbers("") is None
    assert version_numbers(None) is None


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"format": "other"}, "format"),
        ({"layer": "site"}, "layer"),
        ({"extra": 1}, "unknown field"),
        ({"match": {"manufacturer": "X", "model": ["Y"]}}, "unknown field"),
        ({"layer": "model", "match": {"manufacturer": "X"}}, "missing model"),
        ({"layer": "firmware", "match": {"manufacturer": "X", "firmware": {}}}, "min, max"),
        ({"quirks": [q("a", "703.W")] * 1 + [{"id": "b", "point": "703.W", "reason": "r"}]},
         "no change"),
        ({"quirks": [q("a", "W", scale=2)]}, "not a point key"),
        ({"quirks": [q("a", "703.W", scale=0)]}, "non-zero"),
        ({"quirks": [q("a", "703.W", scale=True)]}, "non-zero"),
        ({"quirks": [q("a", "703.W", hide=True, label="x")]}, "hide cannot"),
        ({"quirks": [q("a", "703.W", invert="yes")]}, "true or false"),
        ({"quirks": [q("a b", "703.W", invert=True)]}, "quirk id"),
    ],
)  # fmt: skip
def test_bad_files_are_refused(change: dict, message: str) -> None:
    with pytest.raises(QuirkError, match=message):
        QuirkSet.from_json({**quirk_set(), **change})


def test_duplicate_ids_refused(tmp_path: Path) -> None:
    (tmp_path / "a.json").write_text(json.dumps(quirk_set(quirks=[q("x", "1.W", scale=2)])))
    (tmp_path / "b.json").write_text(
        json.dumps(quirk_set(set_id="other", quirks=[q("x", "1.W", scale=2)]))
    )
    with pytest.raises(QuirkError, match="quirk id 'x' is used twice"):
        load_sets([tmp_path])


def test_file_error_names_the_file(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{")
    with pytest.raises(QuirkError, match="bad.json"):
        load_sets([path])


@pytest.mark.parametrize(
    ("layer", "match", "accepted"),
    [
        ("vendor", {"manufacturer": "ExampleMaker"}, True),
        ("vendor", {"manufacturer": "OtherMaker"}, False),
        ("model", {"manufacturer": "ExampleMaker", "model": ["ExampleModel"]}, True),
        ("model", {"manufacturer": "ExampleMaker", "model": ["Other"]}, False),
        ("model", {"manufacturer": "ExampleMaker", "model": ["ExampleModel"], "options": ["X"]},
         False),
        ("firmware", {"manufacturer": "ExampleMaker", "firmware": {"min": "V1R02B00"}}, True),
        ("firmware", {"manufacturer": "ExampleMaker", "firmware": {"max": "V1R02B03"}}, True),
        ("firmware", {"manufacturer": "ExampleMaker", "firmware": {"max": "V1R02B02"}}, False),
        ("firmware", {"manufacturer": "ExampleMaker", "firmware": {"min": "V2"}}, False),
        ("firmware", {"manufacturer": "ExampleMaker", "model": ["Other"],
                      "firmware": {"min": "V1"}}, False),
    ],
)  # fmt: skip
def test_match(layer: str, match: dict, accepted: bool) -> None:
    found = active(quirk_set(layer, match))
    assert (len(found.sets) == 1) is accepted
    assert (found.not_matched == []) is accepted


def test_firmware_set_needs_a_version() -> None:
    ident = DeviceIdentity("ExampleMaker", "ExampleModel", None, None, "SN", 1)
    found = active(quirk_set("firmware", {"manufacturer": "ExampleMaker",
                                          "firmware": {"min": "1"}}), identity=ident)  # fmt: skip
    assert found.sets == []


def test_scale_units_label_and_source_listed() -> None:
    found = active(quirk_set(quirks=[q("kw", "103.W", scale=0.001, units="kW", label="Power")]))
    out = found.apply(state("103.W", 3252))
    assert (out.value, out.units, out.label, out.quirks) == (3.252, "kW", "Power", ("kw",))
    [entry] = found.report()["quirks"]
    assert (entry["state"], entry["source"], entry["layer"]) == ("active", "made up for tests",
                                                                 "vendor")  # fmt: skip


def test_untouched_point_is_unchanged() -> None:
    found = active(quirk_set(quirks=[q("kw", "103.W", scale=0.001)]))
    point = state("103.VA", 5)
    assert found.apply(point) is point


def test_invert() -> None:
    found = active(quirk_set(quirks=[q("neg", "714.DCW", invert=True)]))
    assert found.apply(state("714.DCW", 250)).value == -250


def test_patterns_cover_groups_and_repeated_models() -> None:
    found = active(quirk_set(quirks=[q("dcw", "160.module[*].DCW", label="MPPT power"),
                                     q("w", "701.W", invert=True),
                                     q("w2", "702#2.W", invert=True)]))  # fmt: skip
    assert found.apply(state("160.module[2].DCW", 1)).label == "MPPT power"
    assert found.apply(state("160.module[2].DCA", 1)).quirks == ()
    assert found.apply(state("701#2.W", 5)).value == -5
    assert found.apply(state("702.W", 5)).value == 5
    assert found.apply(state("702#2.W", 5)).value == -5


def test_higher_layer_overrides_change_by_change() -> None:
    vendor = quirk_set(quirks=[q("v", "103.W", scale=0.001, units="kW", label="Power")])
    firmware = quirk_set(
        "firmware",
        {"manufacturer": "ExampleMaker", "firmware": {"min": "V1"}},
        [q("f", "103.W", scale=1, units="W")],
    )
    found = active(firmware, vendor)  # file order does not matter; layer order does
    out = found.apply(state("103.W", 3252))
    assert (out.value, out.units, out.label, out.quirks) == (3252, "W", "Power", ("f", "v"))


def test_switched_off_falls_back_to_layer_below() -> None:
    vendor = quirk_set(quirks=[q("v", "103.W", scale=0.001, units="kW")])
    firmware = quirk_set(
        "firmware",
        {"manufacturer": "ExampleMaker", "firmware": {"min": "V1"}},
        [q("f", "103.W", scale=1, units="W")],
    )
    found = active(vendor, firmware, off=["f"])
    out = found.apply(state("103.W", 3252))
    assert (out.value, out.units, out.quirks) == (3.252, "kW", ("v",))
    states = {e["id"]: e["state"] for e in found.report()["quirks"]}
    assert states == {"v": "active", "f": "off"}


def test_wholly_overridden_quirk_is_reported_as_such() -> None:
    vendor = quirk_set(quirks=[q("v", "103.W", scale=0.001, units="kW")])
    firmware = quirk_set(
        "firmware",
        {"manufacturer": "ExampleMaker", "firmware": {"min": "V1"}},
        [q("f", "103.W", scale=1, units="W")],
    )
    found = active(vendor, firmware)
    assert found.apply(state("103.W", 3252)).quirks == ("f",)
    states = {e["id"]: e["state"] for e in found.report()["quirks"]}
    assert states == {"v": "overridden", "f": "active"}


def test_unknown_off_id_refused() -> None:
    with pytest.raises(QuirkError, match="no-such"):
        active(quirk_set(quirks=[q("v", "103.W", scale=2)]), off=["no-such"])


def test_same_layer_clash_fails_both_and_gives_no_value() -> None:
    a = quirk_set(quirks=[q("a", "103.W", scale=2)], set_id="a")
    b = quirk_set(quirks=[q("b", "103.W", scale=3)], set_id="b")
    found = active(a, b)
    assert found.apply(state("103.W", 10)).value is None
    states = {e["id"]: (e["state"], e["error"]) for e in found.report()["quirks"]}
    assert states["a"][0] == states["b"][0] == "failing"
    assert "clashes" in states["a"][1]


class Status(IntEnum):
    OK = 1


@pytest.mark.parametrize("value", [Status.OK, "text", True, {"value": 1}])
def test_scale_on_non_number_fails(value) -> None:
    found = active(quirk_set(quirks=[q("s", "103.St", scale=2)]))
    assert found.apply(state("103.St", value)).value is None
    [entry] = found.report()["quirks"]
    assert entry["state"] == "failing"
    assert "not a number" in entry["error"]


def test_unavailable_value_stays_unavailable() -> None:
    found = active(quirk_set(quirks=[q("s", "103.W", scale=2)]))
    assert found.apply(state("103.W", None)).value is None
    assert found.report()["quirks"][0]["state"] == "active"


def test_hide_and_unused() -> None:
    found = active(quirk_set(quirks=[q("h", "103.Evt2", hide=True), q("u", "999.X", scale=2)]))
    assert found.apply(state("103.Evt2", 0)) is None
    states = {e["id"]: e["state"] for e in found.report()["quirks"]}
    assert states == {"h": "active", "u": "unused"}


def test_through_the_service_and_api(mock_modbus_unit: MockModbusUnit) -> None:
    load_device(mock_modbus_unit)
    sets = [
        QuirkSet.from_json(quirk_set(quirks=[q("soc", "713.SoC", scale=0.01, units="ratio"),
                                             q("hide", "713.WHRtg", hide=True)])),
        QuirkSet.from_json(quirk_set(match={"manufacturer": "OtherMaker"}, set_id="other")),
    ]  # fmt: skip
    service = DeviceService(
        "unit1", mock_modbus_unit, interval=60, reads=1, read_interval=0, quirk_sets=sets
    )
    asyncio.run(service.setup())
    client = TestClient(create_app({"unit1": service}, [TOKEN]))
    points = client.get("/api/v1/devices/unit1/points", headers=AUTH).json()["points"]
    assert points["713.SoC"]["value"] == 0.875
    assert points["713.SoC"]["units"] == "ratio"
    assert points["713.SoC"]["quirks"] == ["soc"]
    assert points["713.WHAvail"]["quirks"] == []
    assert "713.WHRtg" not in points
    body = client.get("/api/v1/devices/unit1/quirks", headers=AUTH).json()
    assert [s["id"] for s in body["sets"]] == ["test-vendor"]
    assert body["not_matched"] == ["other"]
    assert {e["id"]: e["state"] for e in body["quirks"]} == {"soc": "active", "hide": "active"}
