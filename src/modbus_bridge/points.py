"""Read every model in a SunSpec chain as points with their standard SunSpec names."""

from __future__ import annotations

import logging
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from modbus_connection import ModbusExceptionError, ModbusUnit
from modbus_connection.model import Component
from modbus_connection.model.sunspec import SunSpecError, SunSpecModel

# The generator's own naming rule, so point names map to its attributes exactly.
from modbus_connection.model.sunspec.generate import _snake

from . import sunspec_models

_LOGGER = logging.getLogger(__name__)

#: The generator merges same-shaped sibling groups into one group of this name.
_MERGED_GROUP = "region"


@dataclass(frozen=True)
class Point:
    """One SunSpec point. ``value`` is ``None`` when the device does not report it."""

    key: str
    """Where the point sits, e.g. ``701.W`` or ``705.Crv[1].Pt[2].V``."""
    model_id: int
    name: str
    """The standard SunSpec point name, e.g. ``W``."""
    label: str | None
    units: str | None
    description: str | None
    writable: bool
    value: Any
    sunspec_type: str | None = None
    """The SunSpec point type, e.g. ``int16``, ``acc32``, ``enum16``."""


@dataclass(frozen=True)
class ModelReading:
    """The points read from one model, or the reason none could be read."""

    model: SunSpecModel
    prefix: str
    """``701``, or ``701#2`` for the second 701 in the chain."""
    points: list[Point]
    error: str | None = None


def _referenced_scale_factors(group: Mapping[str, Any]) -> set[str]:
    """Scale-factor names any point in the model refers to (applied, not shown)."""
    found = {p["sf"] for p in group.get("points", []) if isinstance(p.get("sf"), str)}
    for child in group.get("groups", []):
        found |= _referenced_scale_factors(child)
    return found


def _reported(value: Any) -> Any:
    """SunSpec's "not implemented" for a string is all zeros: give ``None``, not ``""``."""
    if isinstance(value, str):
        return value.strip() or None
    return value


def _field_name(attrs: Sequence[str], point_name: str) -> str:
    """The generated attribute for a SunSpec name (clashes get trailing ``_``)."""
    wanted = _snake(point_name)
    matches = [attr for attr in attrs if attr.rstrip("_") == wanted]
    if len(matches) != 1:
        raise SunSpecError(f"no single generated field for point {point_name!r}: {matches}")
    return matches[0]


def _walk(
    component: Component,
    group: Mapping[str, Any],
    path: str,
    model_id: int,
    scale_factors: set[str],
    top: bool,
) -> Iterator[Point]:
    cls = type(component)
    fields = list(cls.declared_fields)
    for raw in group.get("points", []):
        name = raw["name"]
        if raw["type"] == "pad":
            continue
        if top and name in ("ID", "L"):
            continue  # the model header, checked by the library on every read
        if raw["type"] == "sunssf" and name in scale_factors:
            continue  # already applied to the points that use it
        yield Point(
            key=f"{path}.{name}",
            model_id=model_id,
            name=name,
            label=raw.get("label"),
            units=raw.get("units"),
            description=raw.get("desc"),
            writable=raw.get("access") == "RW",
            value=_reported(getattr(component, _field_name(fields, name))),
            sunspec_type=raw["type"],
        )

    group_attrs = [*cls._static_groups, *cls._repeating_fields]
    children = list(group.get("groups", []))
    index = 0
    while index < len(children):
        child = children[index]
        wanted = _snake(child["name"])
        direct = [attr for attr in group_attrs if attr.rstrip("_") == wanted]
        if direct:
            aliases = [child]
            instances = [getattr(component, direct[0])]
            index += 1
        elif _MERGED_GROUP in group_attrs:
            # This child and the following siblings without their own group
            # were merged, in order, into one repeat.
            aliases = []
            while index < len(children):
                name = _snake(children[index]["name"])
                if any(attr.rstrip("_") == name for attr in group_attrs):
                    break
                aliases.append(children[index])
                index += 1
            merged = getattr(component, _MERGED_GROUP)
            per_alias, remainder = divmod(len(merged), len(aliases))
            if remainder:
                raise SunSpecError(f"{path}: {len(merged)} merged blocks for {len(aliases)} groups")
            instances = [merged[k * per_alias : (k + 1) * per_alias] for k in range(len(aliases))]
        else:
            raise SunSpecError(f"{path}: no generated group for {child['name']!r}")
        for alias, blocks in zip(aliases, instances, strict=True):
            for number, block in enumerate(blocks, start=1):
                yield from _walk(
                    block,
                    alias,
                    f"{path}.{alias['name']}[{number}]",
                    model_id,
                    scale_factors,
                    top=False,
                )


async def read_model(unit: ModbusUnit, model: SunSpecModel, prefix: str) -> ModelReading:
    """Read one model. A model we cannot read gives an error, not guessed values."""
    cls = sunspec_models.component_class(model.model_id)
    definition = sunspec_models.definition(model.model_id)
    if cls is None or definition is None:
        return ModelReading(model, prefix, [], f"no SunSpec definition for model {model.model_id}")
    component = cls(unit, model)
    try:
        await component.async_update()
        await component.async_update_repeating_groups()
        group = definition["group"]
        points = list(
            _walk(
                component,
                group,
                prefix,
                model.model_id,
                _referenced_scale_factors(group),
                top=True,
            )
        )
    except (ModbusExceptionError, SunSpecError) as err:
        _LOGGER.warning("Model %s at %d not read: %s", prefix, model.address, err)
        return ModelReading(model, prefix, [], str(err))
    return ModelReading(model, prefix, points)


async def read_chain(unit: ModbusUnit, chain: Sequence[SunSpecModel]) -> list[ModelReading]:
    """Read every model in the chain, in chain order."""
    seen: dict[int, int] = {}
    readings = []
    for model in chain:
        seen[model.model_id] = seen.get(model.model_id, 0) + 1
        count = seen[model.model_id]
        prefix = str(model.model_id) if count == 1 else f"{model.model_id}#{count}"
        readings.append(await read_model(unit, model, prefix))
    return readings
