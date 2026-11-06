"""Tests for versions (design U5) and the audit log (U8) of user quirks. Values are made up."""

import argparse
import json
from pathlib import Path

import pytest
from modbus_connection.mock import MockModbusUnit
from test_api import AUTH, TOKEN
from test_quirks import q
from test_user_quirks import BASE, make, points, poll

from modbus_bridge.quirks import QuirkError

OTHER = "second-token-not-secret"
AUTH2 = {"Authorization": f"Bearer {OTHER}"}
FIELDS = {"time", "who", "device", "action", "kind", "id", "version", "before", "after", "reason"}


def entries(directory: Path) -> list[dict]:
    return [json.loads(line) for line in (directory / "unit1.audit.jsonl").read_text().splitlines()]


@pytest.fixture
def setup(mock_modbus_unit: MockModbusUnit, tmp_path: Path):
    service, client = make(mock_modbus_unit, tmp_path, tokens=(TOKEN, OTHER))
    return service, client, tmp_path


def test_each_change_adds_one_entry(setup) -> None:
    _, client, directory = setup
    one = q("u-soc", "713.SoC", scale=2, reason="first")
    two = q("u-soc", "713.SoC", scale=3, reason="second")
    assert (
        client.put(f"{BASE}/user-quirks/quirk/u-soc", json=one, headers=AUTH).json()["version"] == 1
    )
    assert (
        client.put(f"{BASE}/user-quirks/quirk/u-soc", json=two, headers=AUTH2).json()["version"]
        == 2
    )
    client.put(f"{BASE}/quirks/ship-soc-label/off?reason=mine is better", headers=AUTH)
    client.delete(f"{BASE}/quirks/ship-soc-label/off", headers=AUTH)
    client.delete(f"{BASE}/user-quirks/quirk/u-soc?reason=not needed", headers=AUTH2)
    log = entries(directory)
    assert all(set(e) == FIELDS and e["device"] == "unit1" for e in log)
    assert [(e["action"], e["who"]) for e in log] == [
        ("save", "token 1"), ("save", "token 2"), ("off", "token 1"), ("on", "token 1"),
        ("remove", "token 2"),
    ]  # fmt: skip
    assert (log[0]["kind"], log[0]["id"], log[0]["version"]) == ("quirk", "u-soc", 1)
    assert (log[0]["before"], log[0]["after"], log[0]["reason"]) == (None, one, "first")
    assert (log[1]["before"], log[1]["after"], log[1]["version"]) == (one, two, 2)
    assert (log[2]["kind"], log[2]["before"], log[2]["after"]) == (None, False, True)
    assert log[2]["reason"] == "mine is better"
    assert (log[3]["before"], log[3]["after"], log[3]["reason"]) == (True, False, None)
    assert (log[4]["before"], log[4]["after"], log[4]["reason"]) == (two, None, "not needed")
    text = (directory / "unit1.audit.jsonl").read_text()
    assert TOKEN not in text and OTHER not in text


def test_versions_carry_on_after_remove_and_restart(
    mock_modbus_unit: MockModbusUnit, tmp_path: Path
) -> None:
    _, client = make(mock_modbus_unit, tmp_path)
    for scale in (2, 3):
        client.put(f"{BASE}/user-quirks/quirk/u-soc", headers=AUTH,
                   json=q("u-soc", "713.SoC", scale=scale, reason=f"x{scale}"))  # fmt: skip
    client.delete(f"{BASE}/user-quirks/quirk/u-soc", headers=AUTH)
    _, client = make(mock_modbus_unit, tmp_path)  # a restart
    answer = client.put(f"{BASE}/user-quirks/quirk/u-soc", headers=AUTH,
                        json=q("u-soc", "713.SoC", scale=4, reason="x4"))  # fmt: skip
    assert answer.json()["version"] == 3
    body = client.get(f"{BASE}/user-quirks/quirk/u-soc/versions", headers=AUTH).json()
    assert [(v["version"], v["reason"], v["item"]["scale"]) for v in body["versions"]] == [
        (1, "x2", 2), (2, "x3", 3), (3, "x4", 4),
    ]  # fmt: skip
    assert all(v["who"] == "token 1" and v["time"] for v in body["versions"])


def test_audit_endpoint_and_filter(setup) -> None:
    _, client, _ = setup
    client.put(f"{BASE}/user-quirks/quirk/u-a", headers=AUTH,
               json=q("u-a", "713.SoC", scale=2, reason="a"))  # fmt: skip
    client.put(f"{BASE}/quirks/ship-soc-label/off", headers=AUTH)
    body = client.get(f"{BASE}/user-quirks/audit", headers=AUTH).json()
    assert [e["id"] for e in body["entries"]] == ["u-a", "ship-soc-label"]
    body = client.get(f"{BASE}/user-quirks/audit?id=u-a", headers=AUTH).json()
    assert [e["id"] for e in body["entries"]] == ["u-a"]
    answer = client.get(f"{BASE}/user-quirks/widget/u-a/versions", headers=AUTH)
    assert answer.status_code == 422


def test_refused_change_adds_no_entry(setup) -> None:
    _, client, directory = setup
    answer = client.put(f"{BASE}/user-quirks/quirk/u-a", headers=AUTH,
                        json=q("u-a", "713.SoC", scale=0, reason="bad"))  # fmt: skip
    assert answer.status_code == 422
    assert client.put(f"{BASE}/quirks/no-such/off", headers=AUTH).status_code == 422
    assert not (directory / "unit1.audit.jsonl").exists()


def test_failed_log_write_changes_nothing(setup) -> None:
    service, client, directory = setup
    client.put(f"{BASE}/user-quirks/quirk/u-a", headers=AUTH,
               json=q("u-a", "713.SoC", label="Mine", reason="a"))  # fmt: skip
    saved = (directory / "unit1.json").read_text()
    (directory / "unit1.audit.jsonl").chmod(0o444)
    try:
        answer = client.put(f"{BASE}/user-quirks/quirk/u-b", headers=AUTH,
                            json=q("u-b", "713.SoC", scale=2, reason="b"))  # fmt: skip
    finally:
        (directory / "unit1.audit.jsonl").chmod(0o644)
    assert answer.status_code == 500
    assert "the change was not made" in answer.json()["detail"]
    assert (directory / "unit1.json").read_text() == saved
    poll(service)
    assert points(client)["713.SoC"]["value"] == 87.5
    assert len(entries(directory)) == 1


def test_broken_log_stops_start_up(tmp_path: Path) -> None:
    from modbus_bridge.serve import build

    (tmp_path / "token").write_text("not-secret\n")
    (tmp_path / "user").mkdir()
    (tmp_path / "user" / "unit1.audit.jsonl").write_text('{"action": "save"}\n')
    args = argparse.Namespace(
        token_file=tmp_path / "token", pics=None, quirks=[], quirk_off=[],
        device_host="192.0.2.10", device_port=502, timeout=1.0, device_id=None, unit=1,
        interval=5.0, user_quirks=tmp_path / "user",
    )  # fmt: skip
    with pytest.raises(QuirkError, match="unit1.audit.jsonl: line 1"):
        build(args)


def test_log_endpoints_off_without_user_quirks_dir(mock_modbus_unit: MockModbusUnit) -> None:
    _, client = make(mock_modbus_unit, None)
    assert client.get(f"{BASE}/user-quirks/audit", headers=AUTH).status_code == 409
    answer = client.get(f"{BASE}/user-quirks/quirk/u-a/versions", headers=AUTH)
    assert answer.status_code == 409
