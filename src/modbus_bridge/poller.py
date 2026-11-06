"""Keep one device's implemented points up to date, and report what changed.

A failed read never keeps an old value or gives 0: the points it covers become
unavailable (``value`` is ``None``) until they read again (rule 8, design D6.2).
"""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Any

from modbus_connection import ModbusError, ModbusUnit
from modbus_connection.model.sunspec import SunSpecModel

from .implemented import ImplementedPoints
from .points import ModelReading, read_chain
from .quirks import ActiveQuirks
from .raw import RawResult, read_raw

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
    trace: Mapping[str, Any] | None = field(default=None, compare=False)
    """For a rule's output: the rule, its inputs and the constants used."""
    options: tuple[Any, ...] | None = None
    """For a rule's output: the only values it can have, if the rule lists them."""
    total: bool = False
    """The value only counts up over the device's life (a lifetime energy total)."""

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
        self._last_readings: list[ModelReading] = []
        self._last_raw: dict[str, RawResult] = {}
        self.removed: list[str] = []
        """Keys the last poll took out of the snapshot (a quirk no longer gives them)."""

    @property
    def implemented(self) -> ImplementedPoints:
        return self._implemented

    @property
    def snapshot(self) -> Mapping[str, PointState]:
        return MappingProxyType(self._snapshot)

    async def poll(self) -> list[PointState]:
        """Read the chain once. Return the states that changed, in key order."""
        quirks = self.quirks  # the same quirks for the whole poll, even if replaced meanwhile
        raw_readings = [] if quirks is None else quirks.readings
        try:
            readings = await read_chain(self._unit, self._chain)
            raw = await read_raw(self._unit, raw_readings) if raw_readings else {}
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
        self._last_readings, self._last_raw = list(readings), dict(raw)
        return self._apply(self._build(readings, raw, quirks), failed_models=failed)

    def preview(
        self, quirks: ActiveQuirks, extra_raw: Mapping[str, RawResult] | None = None
    ) -> dict[str, PointState]:
        """The points the last poll would have given with other quirks. Nothing is read."""
        raw = {**self._last_raw, **(extra_raw or {})}
        return self._build(self._last_readings, raw, quirks)

    def _build(
        self,
        readings: Sequence[ModelReading],
        raw: Mapping[str, RawResult],
        quirks: ActiveQuirks | None,
    ) -> dict[str, PointState]:
        states = self._states(readings, quirks)
        if quirks is not None:
            for state in quirks.raw_states(raw):
                changed = quirks.apply(state)
                if changed is not None:
                    states[state.key] = changed
            for state in quirks.engine.evaluate(states):
                changed = quirks.apply(state)
                if changed is not None:
                    states[state.key] = changed
        return states

    def _states(
        self, readings: Sequence[ModelReading], quirks: ActiveQuirks | None
    ) -> dict[str, PointState]:
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
        if quirks is None:
            return states
        result: dict[str, PointState] = {}
        for key, state in states.items():
            changed = quirks.apply(state)
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
        # Anything a consumer shows counts (value, label, units, options, quirks);
        # only the trace is left out of the comparison.
        changed = [
            state
            for key, state in sorted(new.items())
            if key not in self._snapshot or self._snapshot[key] != state
        ]
        # A point that failed to read was kept above, so only points no longer built go.
        self.removed = sorted(self._snapshot.keys() - new.keys())
        for key in self.removed:
            _LOGGER.info("Point %s removed: the active quirks no longer give it", key)
        self._snapshot = new
        return changed
