"""One device kept up to date in the background, with change subscribers (design D9).

The service owns the poller for one unit. The caller owns the Modbus connection
(rule 7: one connection per device), so tests can pass a mock unit.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import Sequence
from enum import Enum, Flag
from typing import Any

from modbus_connection import ModbusUnit

from .implemented import ImplementedPoints, discover_implemented
from .pics import PicsProfile, apply_pics
from .poller import PointState, Poller
from .sunspec import SunSpecDevice, discover

_LOGGER = logging.getLogger(__name__)

#: Changes a slow subscriber may fall behind by before it is dropped. A dropped
#: subscriber reconnects and starts again from a snapshot.
QUEUE_SIZE = 2000


def json_value(value: Any) -> Any:
    """A point value as JSON: enums and flags keep their number and their names."""
    if value is None or isinstance(value, (bool, str)):
        return value
    if isinstance(value, Flag):
        names = [m.name for m in type(value) if m.value and m in value]
        return {"value": int(value), "names": names}
    if isinstance(value, Enum):
        return {"value": int(value.value), "name": value.name}
    if isinstance(value, (int, float)):
        return value
    return str(value)


def point_json(state: PointState) -> dict[str, Any]:
    return {
        "key": state.key,
        "name": state.name,
        "label": state.label,
        "units": state.units,
        "writable": state.writable,
        "type": state.sunspec_type,
        "value": json_value(state.value),
        "available": state.available,
    }


class DeviceService:
    """Discover one unit, then poll it on a timer and tell subscribers what changed."""

    def __init__(
        self,
        device_id: str,
        unit: ModbusUnit,
        *,
        interval: float,
        profile: PicsProfile | None = None,
        reads: int = 3,
        read_interval: float = 1.0,
    ) -> None:
        self.device_id = device_id
        self._unit = unit
        self._interval = interval
        self._profile = profile
        self._reads = reads
        self._read_interval = read_interval
        self.device: SunSpecDevice | None = None
        self.poller: Poller | None = None
        self.sequence = 0
        self._subscribers: set[asyncio.Queue[tuple[int, list[PointState]] | None]] = set()
        self._task: asyncio.Task[None] | None = None

    @property
    def implemented(self) -> ImplementedPoints:
        if self.poller is None:
            raise RuntimeError("service not started")
        return self.poller.implemented

    async def setup(self) -> None:
        """Discover the device and its implemented points, then poll once."""
        self.device = await discover(self._unit)
        implemented, _ = await discover_implemented(
            self._unit, self.device.chain, self._reads, self._read_interval
        )
        if self._profile is not None:
            implemented, _ = apply_pics(implemented, self._profile)
        self.poller = Poller(self._unit, self.device.chain, implemented)
        await self.poll_once()

    async def poll_once(self) -> list[PointState]:
        if self.poller is None:
            raise RuntimeError("service not started")
        changes = await self.poller.poll()
        if changes:
            self.sequence += 1
            self._publish(self.sequence, changes)
        return changes

    def start(self) -> None:
        """Poll in the background every ``interval`` seconds."""
        self._task = asyncio.create_task(self._run(), name=f"poll {self.device_id}")

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
        for queue in list(self._subscribers):
            self._close(queue)

    async def _run(self) -> None:
        while True:
            await asyncio.sleep(self._interval)
            try:
                await self.poll_once()
            except Exception:
                _LOGGER.exception("Poll of %s failed unexpectedly", self.device_id)

    def subscribe(self) -> asyncio.Queue[tuple[int, list[PointState]] | None]:
        queue: asyncio.Queue[tuple[int, list[PointState]] | None] = asyncio.Queue(QUEUE_SIZE)
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[Any]) -> None:
        self._subscribers.discard(queue)

    def _publish(self, sequence: int, changes: Sequence[PointState]) -> None:
        for queue in list(self._subscribers):
            try:
                queue.put_nowait((sequence, list(changes)))
            except asyncio.QueueFull:
                _LOGGER.warning("Dropping a slow subscriber of %s", self.device_id)
                self._close(queue)

    def _close(self, queue: asyncio.Queue[Any]) -> None:
        """End a subscriber's stream; ``None`` tells it to stop."""
        self._subscribers.discard(queue)
        with contextlib.suppress(asyncio.QueueFull):
            queue.put_nowait(None)
