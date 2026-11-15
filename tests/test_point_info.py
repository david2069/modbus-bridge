"""Tests for where each point is read and what the PICS says (P2U step 20). Values are made up."""

import asyncio
import importlib.util
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from modbus_connection.mock import MockModbusUnit
from modbus_connection.model.sunspec import SunSpecModel
from test_api import AUTH, M713, TOKEN, client, load_device, service  # noqa: F401 (fixtures)
from test_pics import _profile
from test_points import model_713
from test_quirks import quirk_set

from modbus_bridge.api import create_app
from modbus_bridge.pics import pics_status
from modbus_bridge.points import read_chain, read_model
from modbus_bridge.quirks import ActiveQuirks, QuirkSet
from modbus_bridge.raw import RawResult
from modbus_bridge.service import DeviceService
from modbus_bridge.sunspec import DeviceIdentity, discover

_PATH = Path(__file__).parent.parent / "scripts" / "sunspec_sim.py"
_SPEC = importlib.util.spec_from_file_location("sunspec_sim_info", _PATH)
assert _SPEC and _SPEC.loader
sim = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(sim)


def test_every_address_holds_that_points_registers(mock_modbus_unit: MockModbusUnit) -> None:
    """The made-up inverter (models 1, 103, 120 and 160 with 2 repeating modules):
    the registers at each point's address are exactly that point's raw value."""
    models = sim.inverter_models(0)
    regs = sim.build_map(models)
    mock_modbus_unit.holding[sim.BASE_ADDRESS] = regs
    device = asyncio.run(discover(mock_modbus_unit))
    readings = asyncio.run(read_chain(mock_modbus_unit, device.chain))
    values = {str(model_id): v for model_id, v, _ in models}
    checked = 0
    for reading in readings:
        assert reading.error is None
        for point in reading.points:
            assert point.address is not None and point.size is not None, point.key
            start = point.address - sim.BASE_ADDRESS
            prefix, path = point.key.split(".", 1)
            raw = next(p for p in _definition_points(point.model_id, path))
            expected = sim.encode(raw["type"], raw["size"], values[prefix].get(path))
            assert regs[start : start + point.size] == expected, point.key
            checked += 1
    assert checked > 60
    keys = {p.key: p for r in readings for p in r.points}
    assert keys["160.module[2].DCW"].address == keys["160.module[1].DCW"].address + 20


def _definition_points(model_id: int, path: str):
    """The definition entry for a point path such as ``module[2].DCW``."""
    from modbus_bridge.sunspec_models import definition

    group = definition(model_id)["group"]
    *groups, name = path.split(".")
    for part in groups:
        group = next(g for g in group["groups"] if g["name"] == part.split("[")[0])
    yield from (p for p in group["points"] if p["name"] == name)


def test_layout_that_does_not_fill_the_model_gives_no_addresses(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    block = model_713()
    block[1] = 8  # one register longer than the definition
    mock_modbus_unit.holding[40000] = [*block, 0]
    reading = asyncio.run(read_model(mock_modbus_unit, SunSpecModel(713, 40000, 8), "713"))
    assert reading.points and all(p.address is None and p.size is None for p in reading.points)


def test_raw_reading_keeps_its_address_and_table() -> None:
    reading = {"id": "r1", "name": "x", "reason": "test", "address": 1000, "type": "uint32",
               "table": "input"}  # fmt: skip
    qs = QuirkSet.from_json(quirk_set(quirks=[]) | {"readings": [reading]})
    who = DeviceIdentity("ExampleMaker", "ExampleModel", None, "1.0.0", "SN-PLACEHOLDER", 1)
    quirks = ActiveQuirks([qs], who, [])
    [state] = quirks.raw_states({"r1": RawResult(5, None)})
    assert (state.address, state.size, state.table) == (1000, 2, "input")


@pytest.mark.parametrize(
    ("key", "status"),
    [("713.WHRtg", "implemented"), ("713#2.SoC", "implemented"), ("713.Sta", "unimplemented"),
     ("713.WHAvail", "not listed"), ("701.W", "model not covered"), ("label.x", None),
     ("raw.x", None)],
)  # fmt: skip
def test_pics_status(key: str, status: str | None) -> None:
    assert pics_status(_profile(), key) == status
    assert pics_status(None, key) is None


def test_point_info_route(client: TestClient) -> None:  # noqa: F811
    answer = client.get("/api/v1/devices/unit1/point-info", headers=AUTH).json()
    assert answer["pics"] is None
    soc = answer["points"]["713.SoC"]
    assert soc == {"address": M713 + 4, "size": 1, "table": "holding", "pics": None,
                   "certified": None, "min": None, "max": None, "ha_default": True}  # fmt: skip
    assert answer["points"]["1.Mn"]["address"] == 40004
    assert answer["points"]["1.Mn"]["size"] == 16
    points = client.get("/api/v1/devices/unit1/points", headers=AUTH).json()["points"]
    assert set(answer["points"]) == set(points)


def test_point_info_with_pics(mock_modbus_unit: MockModbusUnit) -> None:
    load_device(mock_modbus_unit)
    svc = DeviceService("unit1", mock_modbus_unit, interval=60, reads=1, read_interval=0,
                        profile=_profile())  # fmt: skip
    asyncio.run(svc.setup())
    app = TestClient(create_app({"unit1": svc}, [TOKEN]))
    answer = app.get("/api/v1/devices/unit1/point-info", headers=AUTH).json()
    assert answer["pics"] == {"certificate": "SM-TEST", "source_url": None}
    assert answer["points"]["713.SoC"]["pics"] == "implemented"
    assert answer["points"]["1.Mn"]["pics"] == "model not covered"
    whrtg = answer["points"]["713.WHRtg"]
    assert (whrtg["certified"], whrtg["min"], whrtg["max"]) == (13600, 0, 20000)
    assert answer["points"]["713.SoC"]["certified"] is None


def test_ha_default_follows_the_publisher(mock_modbus_unit: MockModbusUnit) -> None:
    load_device(mock_modbus_unit)
    mock_modbus_unit.holding[1000] = [5]
    reading = {"id": "r1", "name": "x", "reason": "test", "address": 1000, "type": "uint16"}
    rule = {"id": "n1", "output": "y", "label": "Y", "inputs": {"v": "raw.x"}, "formula": "v",
            "reason": "test"}  # fmt: skip
    qs = QuirkSet.from_json(quirk_set(quirks=[]) | {"readings": [reading], "rules": [rule]})
    svc = DeviceService("unit1", mock_modbus_unit, interval=60, reads=1, read_interval=0,
                        quirk_sets=[qs])  # fmt: skip
    asyncio.run(svc.setup())
    points = svc.point_info()["points"]
    assert points["713.SoC"]["ha_default"] is True
    assert points["label.y"]["ha_default"] is True
    assert points["raw.x"]["ha_default"] is False
    assert points["1.Mn"]["ha_default"] is False


def test_point_info_needs_a_token(client: TestClient) -> None:  # noqa: F811
    assert client.get("/api/v1/devices/unit1/point-info").status_code == 401
