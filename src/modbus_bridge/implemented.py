"""Which points a device implements (design D6), discovered by reading it several times.

A point is implemented if it gave a value on any read. It is not implemented
only if it gave SunSpec's "not implemented" value on every read. A point that
later gives a value becomes implemented, and this is logged (D6.4).
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence
from dataclasses import dataclass, replace

from modbus_connection import ModbusUnit
from modbus_connection.model.sunspec import SunSpecModel

from .points import ModelReading, read_chain

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ImplementedPoints:
    """The sorted point keys, and where the sorting came from."""

    source: str
    """E.g. ``discovered over 3 reads``."""
    implemented: frozenset[str]
    not_implemented: frozenset[str]
    unreadable_models: tuple[str, ...]
    """Models that failed on every read; their points are in neither set."""

    def update(self, readings: Sequence[ModelReading]) -> tuple[ImplementedPoints, list[str]]:
        """Promote any not-implemented point that now has a value.

        Returns the updated set and the keys promoted.
        """
        promoted = sorted(
            point.key
            for reading in readings
            for point in reading.points
            if point.value is not None and point.key in self.not_implemented
        )
        for key in promoted:
            _LOGGER.info("Point %s now gives a value: implemented", key)
        if not promoted:
            return self, []
        updated = replace(
            self,
            implemented=self.implemented | set(promoted),
            not_implemented=self.not_implemented - set(promoted),
        )
        return updated, promoted


def sort_points(rounds: Sequence[Sequence[ModelReading]], source: str) -> ImplementedPoints:
    """Sort every point seen in ``rounds`` into implemented or not implemented."""
    implemented: set[str] = set()
    seen: set[str] = set()
    read_ok: set[str] = set()
    all_models: list[str] = []
    for readings in rounds:
        for reading in readings:
            if reading.prefix not in all_models:
                all_models.append(reading.prefix)
            if reading.error is None:
                read_ok.add(reading.prefix)
            for point in reading.points:
                seen.add(point.key)
                if point.value is not None:
                    implemented.add(point.key)
    return ImplementedPoints(
        source=source,
        implemented=frozenset(implemented),
        not_implemented=frozenset(seen - implemented),
        unreadable_models=tuple(p for p in all_models if p not in read_ok),
    )


async def discover_implemented(
    unit: ModbusUnit, chain: Sequence[SunSpecModel], reads: int, interval: float
) -> tuple[ImplementedPoints, list[ModelReading]]:
    """Read the chain ``reads`` times, ``interval`` seconds apart, and sort the points.

    Returns the sorted points and the last round of readings.
    """
    if reads < 1:
        raise ValueError("reads must be at least 1")
    rounds: list[list[ModelReading]] = []
    for number in range(reads):
        if number:
            await asyncio.sleep(interval)
        rounds.append(await read_chain(unit, chain))
    result = sort_points(rounds, f"discovered over {reads} reads")
    _LOGGER.info(
        "%d implemented, %d not implemented (%s)",
        len(result.implemented),
        len(result.not_implemented),
        result.source,
    )
    return result, rounds[-1]


def implemented_only(
    readings: Sequence[ModelReading], points: ImplementedPoints
) -> list[ModelReading]:
    """Drop the not-implemented points; keep everything else, errors included."""
    return [
        replace(reading, points=[p for p in reading.points if p.key not in points.not_implemented])
        for reading in readings
    ]
