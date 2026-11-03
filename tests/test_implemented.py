"""Tests for sorting points into implemented and not implemented (design D6).

All values are made up for the test.
"""

import asyncio

from modbus_connection.encode import encode_string
from modbus_connection.mock import MockModbusUnit
from modbus_connection.model.sunspec import SunSpecModel

from modbus_bridge.implemented import implemented_only, sort_points
from modbus_bridge.points import ModelReading, Point, read_model
from modbus_bridge.probe import UNAVAILABLE, format_readings

MODEL = SunSpecModel(model_id=713, address=40000, length=7)


def point(key: str, value: object) -> Point:
    return Point(key, 713, key.split(".")[-1], None, None, None, False, value)


def reading(*points: Point, error: str | None = None, prefix: str = "713") -> ModelReading:
    return ModelReading(MODEL, prefix, list(points), error)


def test_value_on_any_read_is_implemented() -> None:
    rounds = [
        [reading(point("713.SoC", None), point("713.SoH", None))],
        [reading(point("713.SoC", 50.0), point("713.SoH", None))],
    ]
    result = sort_points(rounds, "test")
    assert result.implemented == {"713.SoC"}
    assert result.not_implemented == {"713.SoH"}


def test_model_failing_every_read_is_in_neither_set() -> None:
    rounds = [
        [reading(error="refused"), reading(point("1.Mn", "X"), prefix="1")],
        [reading(error="refused"), reading(point("1.Mn", "X"), prefix="1")],
    ]
    result = sort_points(rounds, "test")
    assert result.unreadable_models == ("713",)
    assert result.implemented == {"1.Mn"}
    assert result.not_implemented == frozenset()


def test_later_value_promotes_point() -> None:
    result = sort_points([[reading(point("713.SoH", None))]], "test")
    updated, promoted = result.update([reading(point("713.SoH", 99.0))])
    assert promoted == ["713.SoH"]
    assert "713.SoH" in updated.implemented
    assert "713.SoH" not in updated.not_implemented


def test_only_implemented_points_shown_and_unavailable_label() -> None:
    first = [reading(point("713.SoC", 50.0), point("713.SoH", None))]
    result = sort_points([first], "test")
    # SoC is implemented but gives no value on a later read: unavailable, not hidden.
    later = [reading(point("713.SoC", None), point("713.SoH", None))]
    shown = implemented_only(later, result)
    assert [p.key for p in shown[0].points] == ["713.SoC"]
    text = format_readings(later, result, show_not_implemented=True)
    assert f"713.SoC                      {UNAVAILABLE}" in text
    assert "Not implemented (1):\n  713.SoH" in text


def test_all_zero_string_is_none(mock_modbus_unit: MockModbusUnit) -> None:
    mock_modbus_unit.holding[40000] = [
        1,
        66,
        *encode_string("ExampleMaker", length=16),
        *encode_string("", length=16),  # Md left empty
        *[0] * 34,
    ]
    model = SunSpecModel(model_id=1, address=40000, length=66)
    result = asyncio.run(read_model(mock_modbus_unit, model, "1"))
    values = {p.name: p.value for p in result.points}
    assert values["Mn"] == "ExampleMaker"
    assert values["Md"] is None
