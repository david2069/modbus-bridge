"""Tests for the user's own quirks (design L5, 2b) through the REST API. All values are made up."""

import argparse
import asyncio
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from modbus_connection import IllegalDataAddressError
from modbus_connection.mock import MockModbusUnit
from test_api import AUTH, TOKEN, load_device
from test_evaluator import const, rule
from test_quirks import q, quirk_set

from modbus_bridge.api import create_app
from modbus_bridge.quirks import QuirkError, QuirkSet, load_sets
from modbus_bridge.service import DeviceService
from modbus_bridge.user_quirks import UserQuirkStore

BASE = "/api/v1/devices/unit1"
SHIPPED = quirk_set(quirks=[q("ship-soc-label", "713.SoC", label="Battery level")])


def reading(rid: str, address: int, name: str | None = None) -> dict:
    return {"id": rid, "name": name or rid.replace("-", "_"), "address": address,
            "type": "uint16", "reason": "test"}  # fmt: skip


def make(unit: MockModbusUnit, directory: Path | None, off=()) -> tuple[DeviceService, TestClient]:
    load_device(unit)
    unit.holding[1000] = [42, 7]
    unit.fail_read(2000, IllegalDataAddressError(2))
    service = DeviceService(
        "unit1", unit, interval=60, reads=1, read_interval=0,
        quirk_sets=[QuirkSet.from_json(SHIPPED)], quirks_off=list(off),
        user_store=None if directory is None else UserQuirkStore(directory, "unit1"),
    )  # fmt: skip
    asyncio.run(service.setup())
    return service, TestClient(create_app({"unit1": service}, [TOKEN]))


def points(client: TestClient) -> dict:
    return client.get(f"{BASE}/points", headers=AUTH).json()["points"]


def poll(service: DeviceService) -> None:
    asyncio.run(service.poll_once())


@pytest.fixture
def setup(mock_modbus_unit: MockModbusUnit, tmp_path: Path):
    service, client = make(mock_modbus_unit, tmp_path)
    return service, client, tmp_path


def test_save_preview_and_next_poll(setup) -> None:
    service, client, directory = setup
    item = q("u-soc", "713.SoC", scale=0.01, units="fraction", reason="I want a fraction")
    preview = client.post(f"{BASE}/user-quirks/check", json={"kind": "quirk", "item": item},
                          headers=AUTH).json()  # fmt: skip
    [change] = preview["changes"]
    assert change["key"] == "713.SoC"
    assert change["before"] == {"value": 87.5, "units": "Pct", "label": "Battery level"}
    assert change["after"] == {"value": 0.875, "units": "fraction", "label": "Battery level"}
    assert not (directory / "unit1.json").exists()  # check saves nothing
    assert points(client)["713.SoC"]["value"] == 87.5
    answer = client.put(f"{BASE}/user-quirks/quirk/u-soc", json=item, headers=AUTH)
    assert answer.status_code == 200
    poll(service)  # the next reading, no restart
    soc = points(client)["713.SoC"]
    assert (soc["value"], soc["units"]) == (0.875, "fraction")
    assert soc["quirks"] == ["ship-soc-label", "u-soc"]
    entry = next(e for e in client.get(f"{BASE}/quirks", headers=AUTH).json()["quirks"]
                 if e["id"] == "u-soc")  # fmt: skip
    assert (entry["layer"], entry["state"], entry["reason"]) == (
        "user",
        "active",
        "I want a fraction",
    )
    saved = json.loads((directory / "unit1.json").read_text())
    assert saved["items"]["quirks"] == [item]


def test_user_wins_over_shipped_and_remove_falls_back(setup) -> None:
    service, client, _ = setup
    item = q("u-soc-label", "713.SoC", label="My battery", reason="nicer name")
    client.put(f"{BASE}/user-quirks/quirk/u-soc-label", json=item, headers=AUTH)
    poll(service)
    assert points(client)["713.SoC"]["label"] == "My battery"
    answer = client.delete(f"{BASE}/user-quirks/quirk/u-soc-label", headers=AUTH)
    assert answer.status_code == 200
    poll(service)
    assert points(client)["713.SoC"]["label"] == "Battery level"
    assert client.delete(f"{BASE}/user-quirks/quirk/u-soc-label", headers=AUTH).status_code == 404


def test_each_kind_create_replace_remove(setup) -> None:
    service, client, _ = setup
    items = [
        ("reading", reading("u-r-a", 1000, "a")),
        ("constant", const("u-c-k", "k", 2)),
        ("rule", rule("u-n-a2", "a2", "a * k", {"a": "raw.a"})),
    ]
    for kind, item in items:
        answer = client.put(f"{BASE}/user-quirks/{kind}/{item['id']}", json=item, headers=AUTH)
        assert answer.status_code == 200, answer.json()
    poll(service)
    assert (points(client)["raw.a"]["value"], points(client)["label.a2"]["value"]) == (42, 84)
    client.put(f"{BASE}/user-quirks/constant/u-c-k", json=const("u-c-k", "k", 3), headers=AUTH)
    poll(service)
    assert points(client)["label.a2"]["value"] == 126
    assert client.get(f"{BASE}/user-quirks", headers=AUTH).json()["items"]["constants"] == [
        const("u-c-k", "k", 3)
    ]
    for kind, item in reversed(items):
        client.delete(f"{BASE}/user-quirks/{kind}/{item['id']}", headers=AUTH)
    poll(service)
    assert "raw.a" not in points(client) and "label.a2" not in points(client)


def test_reading_gets_a_test_read(setup) -> None:
    _, client, _ = setup
    body = {"kind": "reading", "item": reading("u-r-b", 1001, "b")}
    preview = client.post(f"{BASE}/user-quirks/check", json=body, headers=AUTH).json()
    assert preview["test_read"] == 7
    assert preview["changes"][0]["key"] == "raw.b"
    assert preview["changes"][0]["before"] is None
    body = {"kind": "reading", "item": reading("u-r-bad", 2000)}
    answer = client.post(f"{BASE}/user-quirks/check", json=body, headers=AUTH)
    assert answer.status_code == 422
    assert "test read of u-r-bad failed" in answer.json()["detail"]


@pytest.mark.parametrize(
    ("kind", "item", "message"),
    [
        ("quirk", {"id": "u-x", "point": "713.SoC", "scale": 2}, "missing reason"),
        ("quirk", q("u-x", "713.SoC", colour="red"), "unknown field"),
        ("quirk", q("ship-soc-label", "713.SoC", scale=2), "used twice"),
        ("quirk", q("u-x", "713.SoC", scale=0), "scale"),
        ("rule", rule("u-x", "x", "x.real"), "x"),
        ("widget", q("u-x", "713.SoC", scale=2), "kind must be"),
    ],
)
def test_refusals_change_nothing(setup, kind: str, item: dict, message: str) -> None:
    _, client, directory = setup
    answer = client.put(f"{BASE}/user-quirks/{kind}/u-x", json=item | {"id": item["id"]},
                        headers=AUTH)  # fmt: skip
    if item["id"] != "u-x":
        assert answer.status_code == 422
        assert "match the path" in answer.json()["detail"]
        answer = client.put(f"{BASE}/user-quirks/{kind}/{item['id']}", json=item, headers=AUTH)
    assert answer.status_code == 422
    assert message in answer.json()["detail"]
    assert not (directory / "unit1.json").exists()


def test_clash_and_loop_refused(setup) -> None:
    _, client, _ = setup
    client.put(f"{BASE}/user-quirks/quirk/u-a", headers=AUTH,
               json=q("u-a", "713.SoC", scale=2, reason="a"))  # fmt: skip
    answer = client.put(f"{BASE}/user-quirks/quirk/u-b", headers=AUTH,
                        json=q("u-b", "713.SoC", scale=3, reason="b"))  # fmt: skip
    assert answer.status_code == 422
    assert "clashes with u-a" in answer.json()["detail"]
    client.put(f"{BASE}/user-quirks/rule/u-r1", headers=AUTH,
               json=rule("u-r1", "one", "t", {"t": "label.two"}))  # fmt: skip
    answer = client.put(f"{BASE}/user-quirks/rule/u-r2", headers=AUTH,
                        json=rule("u-r2", "two", "o", {"o": "label.one"}))  # fmt: skip
    assert answer.status_code == 422
    assert "loop" in answer.json()["detail"]


def test_switch_off_and_on_is_kept(mock_modbus_unit: MockModbusUnit, tmp_path: Path) -> None:
    service, client = make(mock_modbus_unit, tmp_path)
    assert client.put(f"{BASE}/quirks/ship-soc-label/off", headers=AUTH).status_code == 200
    poll(service)
    assert points(client)["713.SoC"]["label"] != "Battery level"
    assert json.loads((tmp_path / "unit1.json").read_text())["off"] == ["ship-soc-label"]
    assert client.put(f"{BASE}/quirks/no-such/off", headers=AUTH).status_code == 422
    # A restart keeps it off.
    service, client = make(mock_modbus_unit, tmp_path)
    assert points(client)["713.SoC"]["label"] != "Battery level"
    assert client.delete(f"{BASE}/quirks/ship-soc-label/off", headers=AUTH).status_code == 200
    poll(service)
    assert points(client)["713.SoC"]["label"] == "Battery level"


def test_command_line_off_cannot_be_switched_on(
    mock_modbus_unit: MockModbusUnit, tmp_path: Path
) -> None:
    _, client = make(mock_modbus_unit, tmp_path, off=["ship-soc-label"])
    answer = client.delete(f"{BASE}/quirks/ship-soc-label/off", headers=AUTH)
    assert answer.status_code == 422
    assert "--quirk-off" in answer.json()["detail"]


def test_saved_items_survive_a_restart(mock_modbus_unit: MockModbusUnit, tmp_path: Path) -> None:
    _, client = make(mock_modbus_unit, tmp_path)
    client.put(f"{BASE}/user-quirks/quirk/u-soc", headers=AUTH,
               json=q("u-soc", "713.SoC", units="fraction", reason="r"))  # fmt: skip
    _, client = make(mock_modbus_unit, tmp_path)
    assert points(client)["713.SoC"]["units"] == "fraction"


def test_off_without_user_quirks_dir(mock_modbus_unit: MockModbusUnit) -> None:
    _, client = make(mock_modbus_unit, None)
    assert client.get(f"{BASE}/user-quirks", headers=AUTH).json()["enabled"] is False
    answer = client.put(f"{BASE}/user-quirks/quirk/u-a", headers=AUTH,
                        json=q("u-a", "713.SoC", scale=2))  # fmt: skip
    assert answer.status_code == 409
    assert client.put(f"{BASE}/quirks/ship-soc-label/off", headers=AUTH).status_code == 409


def test_bad_file_stops_start_up(tmp_path: Path) -> None:
    from modbus_bridge.serve import build

    (tmp_path / "token").write_text("not-secret\n")
    (tmp_path / "user").mkdir()
    (tmp_path / "user" / "unit1.json").write_text(json.dumps({
        "format": "modbus-bridge/user-quirks", "version": 1, "device": "unit1",
        "items": {"quirks": [{"id": "u-a", "point": "713.SoC", "scale": 2}]}, "off": [],
    }))  # fmt: skip
    args = argparse.Namespace(
        token_file=tmp_path / "token", pics=None, quirks=[], quirk_off=[],
        device_host="192.0.2.10", device_port=502, timeout=1.0, device_id=None, unit=1,
        interval=5.0, user_quirks=tmp_path / "user",
    )  # fmt: skip
    with pytest.raises(QuirkError, match="missing reason"):
        build(args)
    (tmp_path / "user" / "unit1.json").write_text("{not json")
    with pytest.raises(QuirkError, match="unit1.json"):
        build(args)


def test_shipped_file_may_not_use_user_layer(tmp_path: Path) -> None:
    data = quirk_set(quirks=[q("a", "713.SoC", scale=2)]) | {"layer": "user"}
    (tmp_path / "set.json").write_text(json.dumps(data))
    with pytest.raises(QuirkError, match="only for the user's own quirks"):
        load_sets([tmp_path / "set.json"])
