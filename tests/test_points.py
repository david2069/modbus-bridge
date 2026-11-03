"""Tests for reading SunSpec models as points, against modbus-connection's mock.

All values here are made up for the test, not taken from any real device.
"""

import asyncio
from enum import Enum
from pathlib import Path
from typing import Any

import pytest
from modbus_connection import IllegalDataAddressError
from modbus_connection.mock import MockModbusUnit
from modbus_connection.model import Component
from modbus_connection.model.sunspec import SunSpecModel
from modbus_connection.model.sunspec.generate import _snake

from modbus_bridge import sunspec_models
from modbus_bridge.points import (
    _MERGED_GROUP,
    _field_name,
    _referenced_scale_factors,
    read_chain,
    read_model,
)
from modbus_bridge.probe import UNAVAILABLE, format_value

GENERATED = sorted(
    int(p.stem.split("_")[1])
    for p in (Path(sunspec_models.__file__).parent / "generated").glob("model_*.py")
)


def _static_walk(cls: type[Component], group: dict[str, Any], scale_factors: set[str], top: bool):
    """Map every point of a definition to a generated field, without reading."""
    fields = list(cls.declared_fields)
    for raw in group.get("points", []):
        if raw["type"] == "pad" or (top and raw["name"] in ("ID", "L")):
            continue
        if raw["type"] == "sunssf" and raw["name"] in scale_factors:
            continue
        _field_name(fields, raw["name"])  # raises unless exactly one match
    groups = {**cls._static_groups, **cls._repeating_fields}
    for child in group.get("groups", []):
        wanted = _snake(child["name"])
        direct = [attr for attr in groups if attr.rstrip("_") == wanted]
        attr = direct[0] if direct else _MERGED_GROUP
        assert attr in groups, f"no group for {child['name']}"
        _static_walk(groups[attr].component_class, child, scale_factors, top=False)


@pytest.mark.parametrize("model_id", GENERATED)
def test_every_point_maps_to_a_generated_field(model_id: int) -> None:
    cls = sunspec_models.component_class(model_id)
    definition = sunspec_models.definition(model_id)
    assert cls is not None and definition is not None
    group = definition["group"]
    _static_walk(cls, group, _referenced_scale_factors(group), top=True)


def test_catalogue_size() -> None:
    assert len(GENERATED) == 111
    assert sunspec_models.component_class(63001) is None


def model_713(soc: int = 875, soh: int = 0xFFFF) -> list[int]:
    """Model 713 block: header, WHRtg, WHAvail, SoC, SoH, Sta, WH_SF, Pct_SF."""
    return [713, 7, 1350, 600, soc, soh, 1, 1, 0xFFFF]  # WH_SF +1, Pct_SF -1


def test_model_713_scaled_named_and_missing(mock_modbus_unit: MockModbusUnit) -> None:
    mock_modbus_unit.holding[40000] = model_713()
    model = SunSpecModel(model_id=713, address=40000, length=7)
    reading = asyncio.run(read_model(mock_modbus_unit, model, "713"))

    assert reading.error is None
    points = {p.name: p for p in reading.points}
    assert list(points) == ["WHRtg", "WHAvail", "SoC", "SoH", "Sta"]  # SFs applied, not shown
    assert points["WHRtg"].value == pytest.approx(13500)
    assert points["WHRtg"].units == "WH"
    assert points["SoC"].key == "713.SoC"
    assert points["SoC"].value == pytest.approx(87.5)
    assert points["SoC"].label == "State of Charge"
    assert points["SoH"].value is None  # 0xFFFF: not reported
    assert format_value(points["SoH"].value) == UNAVAILABLE
    assert isinstance(points["Sta"].value, Enum)
    assert format_value(points["Sta"].value) == "1 (WARNING)"


def test_model_without_definition_is_not_read(mock_modbus_unit: MockModbusUnit) -> None:
    model = SunSpecModel(model_id=64999, address=40000, length=4)
    reading = asyncio.run(read_model(mock_modbus_unit, model, "64999"))

    assert reading.points == []
    assert reading.error == "no SunSpec definition for model 64999"


def test_refused_model_does_not_stop_the_next(mock_modbus_unit: MockModbusUnit) -> None:
    mock_modbus_unit.holding[40000] = model_713()
    mock_modbus_unit.holding[40009] = model_713(soc=500)
    mock_modbus_unit.fail_read(40000, IllegalDataAddressError(2))
    chain = [
        SunSpecModel(model_id=713, address=40000, length=7),
        SunSpecModel(model_id=713, address=40009, length=7),
    ]
    first, second = asyncio.run(read_chain(mock_modbus_unit, chain))

    assert first.points == [] and first.error
    assert second.error is None
    assert second.prefix == "713#2"
    assert {p.key: p.value for p in second.points}["713#2.SoC"] == pytest.approx(50.0)


@pytest.mark.parametrize(
    ("sta", "shown"),
    [(7, "7 (UNKNOWN)"), (1, "1 (WARNING)"), (0xFFFF, UNAVAILABLE)],
)
def test_enum_value_not_named_by_sunspec_is_kept(
    mock_modbus_unit: MockModbusUnit, sta: int, shown: str
) -> None:
    block = model_713()
    block[6] = sta  # Sta
    mock_modbus_unit.holding[40000] = block
    model = SunSpecModel(model_id=713, address=40000, length=7)
    reading = asyncio.run(read_model(mock_modbus_unit, model, "713"))
    value = {p.name: p.value for p in reading.points}["Sta"]
    assert format_value(value) == shown
    assert sunspec_models.is_unknown(value) == (sta == 7)
