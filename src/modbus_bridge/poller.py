"""Keep one device's implemented points up to date, and report what changed.

A failed read never keeps an old value or gives 0: the points it covers become
unavailable (``value`` is ``None``) until they read again (rule 8, design D6.2).
"""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import Any

from modbus_connection import ModbusError, ModbusUnit
from modbus_connection.model.sunspec import SunSpecModel

from .implemented import ImplementedPoints
from .points import ModelReading, read_chain
from .quirks import ActiveQuirks

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class PointState:
    """The latest state of one implemented point. ``value`` ``None`` means unavailable."""

    key: str
    name: str
    label: str | None
    units: str | None
    writable: bool
    value: Any
    sunspec_type: str | None = None
    quirks: tuple[str, ...] = ()
    """Ids of the quirks applied to this point."""

    @property
    def available(self) -> bool:
        return self.value is not None


def _model_prefix(key: str) -> str:
    return key.split(".", 1)[0]


class Poller:
    """Poll one unit's SunSpec chain and keep a snapshot of its implemented points."""

    def __init__(
        self,
        unit: ModbusUnit,
        chain: Sequence[SunSpecModel],
        implemented: ImplementedPoints,
        quirks: ActiveQuirks | None = None,
    ) -> None:
        self._unit = unit
        self.quirks = quirks
        self._chain = list(chain)
        self._implemented = implemented
        self._snapshot: dict[str, PointState] = {}
        self.last_error: str | None = None

    @property
    def implemented(self) -> ImplementedPoints:
        return self._implemented

    @property
    def snapshot(self) -> Mapping[str, PointState]:
        return MappingProxyType(self._snapshot)

    async def poll(self) -> list[PointState]:
        """Read the chain once. Return the states that changed, in key order."""
        try:
            readings = await read_chain(self._unit, self._chain)
        except ModbusError as err:
            self.last_error = f"{type(err).__name__}: {err}"
            _LOGGER.warning("Poll failed, all points unavailable: %s", self.last_error)
            return self._apply({}, failed_models=None)
        self.last_error = None
        self._implemented, promoted = self._implemented.update(readings)
        failed = {r.prefix for r in readings if r.error is not None}
        for reading in readings:
            if reading.error is not None:
                _LOGGER.warning("Model %s not read: %s", reading.prefix, reading.error)
        return self._apply(self._states(readings), failed_models=failed)

    def _states(self, readings: Sequence[ModelReading]) -> dict[str, PointState]:
        hidden = self._implemented.not_implemented
        states = {
            point.key: PointState(
                key=point.key,
                name=point.name,
                label=point.label,
                units=point.units,
                writable=point.writable,
                value=point.value,
                sunspec_type=point.sunspec_type,
            )
            for reading in readings
            for point in reading.points
            if point.key not in hidden
        }
        if self.quirks is None:
            return states
        result: dict[str, PointState] = {}
        for key, state in states.items():
            changed = self.quirks.apply(state)
            if changed is not None:
                result[key] = changed
        return result

    def _apply(
        self, fresh: dict[str, PointState], failed_models: set[str] | None
    ) -> list[PointState]:
        """Merge a poll into the snapshot; ``failed_models`` None means everything failed."""
        new: dict[str, PointState] = dict(fresh)
        for key, old in self._snapshot.items():
            if key in new:
                continue
            if failed_models is None or _model_prefix(key) in failed_models:
                new[key] = replace(old, value=None)  # not read this time: unavailable
        changed = [
            state
            for key, state in sorted(new.items())
            if key not in self._snapshot or self._snapshot[key].value != state.value
        ]
        self._snapshot = new
        return changed
