"""Tests for exporting a user quirk as a proposal (design U11). All values are made up."""

import json
from pathlib import Path

import pytest
from modbus_connection.mock import MockModbusUnit
from test_api import AUTH, TOKEN
from test_quirks import q
from test_user_quirks import BASE, make

from modbus_bridge.quirks import QuirkSet

URL = f"{BASE}/user-quirks/quirk/u-soc/export"
FIELDS = {"format", "version", "exported", "kind", "id", "reason", "source", "device",
          "switched_off", "effect", "history", "quirk_set"}  # fmt: skip


@pytest.fixture
def setup(mock_modbus_unit: MockModbusUnit, tmp_path: Path):
    service, client = make(mock_modbus_unit, tmp_path)
    one = q("u-soc", "713.SoC", scale=2, reason="first try")
    two = q("u-soc", "713.SoC", scale=2, units="‰", reason="per mille", source="own meter")
    client.put(f"{BASE}/user-quirks/quirk/u-soc", json=one, headers=AUTH)
    client.put(f"{BASE}/user-quirks/quirk/u-soc", json=two, headers=AUTH)
    return service, client, tmp_path, one, two


def test_export_has_reason_source_effect_and_history(setup) -> None:
    _, client, _, one, two = setup
    answer = client.get(URL, headers=AUTH)
    assert answer.status_code == 200
    body = answer.json()
    assert set(body) == FIELDS
    assert (body["format"], body["version"]) == ("modbus-bridge/quirk-proposal", 1)
    assert (body["kind"], body["id"], body["reason"], body["source"]) == (
        "quirk", "u-soc", "per mille", "own meter",
    )  # fmt: skip
    assert body["device"] == {"manufacturer": "ExampleMaker", "model": "ExampleModel",
                              "options": None, "firmware": "1.0.0"}  # fmt: skip
    assert body["switched_off"] is False
    [effect] = body["effect"]
    assert effect["key"] == "713.SoC"
    assert (effect["before"]["value"], effect["before"]["units"]) == (87.5, "Pct")
    assert (effect["after"]["value"], effect["after"]["units"]) == (175.0, "‰")
    history = body["history"]
    assert [(h["action"], h["version"], h["reason"]) for h in history] == [
        ("save", 1, "first try"), ("save", 2, "per mille"),
    ]  # fmt: skip
    assert (history[0]["after"], history[1]["before"], history[1]["after"]) == (one, one, two)


def test_export_holds_nothing_private(setup) -> None:
    _, client, _, _, _ = setup
    body = client.get(URL, headers=AUTH).json()
    text = json.dumps(body)
    for private in ("SN-PLACEHOLDER", "unit1", TOKEN, "token 1"):
        assert private not in text
    assert all(set(h) == {"time", "action", "version", "before", "after", "reason"}
               for h in body["history"])  # fmt: skip


def test_quirk_set_loads_as_a_shipped_set(setup) -> None:
    _, client, _, _, two = setup
    data = client.get(URL, headers=AUTH).json()["quirk_set"]
    loaded = QuirkSet.from_json(data, path="proposal")
    assert (loaded.id, loaded.layer, loaded.source) == ("proposal-u-soc", "model", "own meter")
    assert data["match"] == {"manufacturer": "ExampleMaker", "model": ["ExampleModel"]}
    assert data["quirks"] == [two]
    assert set(data) == {"format", "version", "id", "layer", "match", "source", "quirks"}


def test_without_source_the_set_names_own_measurement(setup) -> None:
    _, client, _, _, _ = setup
    item = q("u-soc", "713.SoC", scale=3, reason="no source")
    client.put(f"{BASE}/user-quirks/quirk/u-soc", json=item, headers=AUTH)
    body = client.get(URL, headers=AUTH).json()
    assert body["source"] is None
    assert body["quirk_set"]["source"] == (
        "user quirk: own measurement on ExampleMaker ExampleModel, firmware 1.0.0"
    )


def test_switched_off_item_has_no_effect(setup) -> None:
    _, client, _, _, _ = setup
    client.put(f"{BASE}/quirks/u-soc/off?reason=checking", headers=AUTH)
    body = client.get(URL, headers=AUTH).json()
    assert body["switched_off"] is True
    assert body["effect"] == []
    assert [h["action"] for h in body["history"]] == ["save", "save", "off"]


def test_errors(setup, mock_modbus_unit: MockModbusUnit) -> None:
    _, client, _, _, _ = setup
    assert client.get(URL).status_code == 401
    missing = client.get(f"{BASE}/user-quirks/quirk/nope/export", headers=AUTH)
    assert missing.status_code == 404
    assert client.get(f"{BASE}/user-quirks/thing/u-soc/export", headers=AUTH).status_code == 422
    _, off = make(mock_modbus_unit, None)
    assert off.get(URL, headers=AUTH).status_code == 409


def test_export_writes_nothing(setup) -> None:
    _, client, directory, _, _ = setup
    before = {p.name: p.read_bytes() for p in directory.iterdir()}
    client.get(URL, headers=AUTH)
    assert {p.name: p.read_bytes() for p in directory.iterdir()} == before
