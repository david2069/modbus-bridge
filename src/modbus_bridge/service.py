"""One device kept up to date in the background, with change subscribers (design D9).

The service owns the poller for one unit. The caller owns the Modbus connection
(rule 7: one connection per device), so tests can pass a mock unit.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import Mapping, Sequence
from enum import Enum, Flag
from typing import Any

from modbus_connection import ModbusUnit

from .implemented import ImplementedPoints, discover_implemented
from .pics import PicsProfile, apply_pics
from .poller import PointState, Poller
from .quirks import ActiveQuirks, QuirkError, QuirkSet, check_off, check_unique
from .raw import read_raw
from .sunspec import SunSpecDevice, discover
from .user_quirks import KINDS, UserQuirks, UserQuirkStore, check_kind

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
        "quirks": list(state.quirks),
        **({"options": list(state.options)} if state.options is not None else {}),
        **({"total": True} if state.total else {}),
        **({"trace": state.trace} if state.trace is not None else {}),
    }


class UserQuirksOff(RuntimeError):
    """The bridge was started without ``--user-quirks``."""


def _view(state: PointState | None) -> dict[str, Any] | None:
    if state is None:
        return None
    return {"value": json_value(state.value), "units": state.units, "label": state.label}


def _diff(
    before: Mapping[str, PointState], after: Mapping[str, PointState]
) -> list[dict[str, Any]]:
    """The points that differ, with their state before and after (design U3)."""
    changes = []
    for key in sorted(before.keys() | after.keys()):
        old, new = _view(before.get(key)), _view(after.get(key))
        if old == new:
            continue
        error = None
        state = after.get(key)
        if state is not None and state.trace is not None:
            error = state.trace.get("error")
        changes.append({"key": key, "before": old, "after": new, "error": error})
    return changes


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
        quirk_sets: Sequence[QuirkSet] = (),
        quirks_off: Sequence[str] = (),
        user_store: UserQuirkStore | None = None,
    ) -> None:
        self.device_id = device_id
        self._unit = unit
        self._interval = interval
        self._profile = profile
        self._reads = reads
        self._read_interval = read_interval
        self._quirk_sets = list(quirk_sets)
        self._quirks_off = list(quirks_off)
        self.quirks: ActiveQuirks | None = None
        self.user_store = user_store
        self.user = UserQuirks()
        self._poll_lock = asyncio.Lock()
        """Taken by each poll and test read, so two never use the connection at once."""
        self._edit_lock = asyncio.Lock()
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
        # Model 1 is read on every connect, so a new firmware picks its quirks here.
        if self.user_store is not None:
            self.user = self.user_store.load()
        self.quirks = self._build(self.user)
        implemented, _ = await discover_implemented(
            self._unit, self.device.chain, self._reads, self._read_interval
        )
        if self._profile is not None:
            implemented, _ = apply_pics(implemented, self._profile)
        self.poller = Poller(self._unit, self.device.chain, implemented, self.quirks)
        await self.poll_once()

    async def poll_once(self) -> list[PointState]:
        if self.poller is None:
            raise RuntimeError("service not started")
        async with self._poll_lock:
            changes = await self.poller.poll()
        if changes:
            self.sequence += 1
            self._publish(self.sequence, changes)
        return changes

    def _build(self, user: UserQuirks) -> ActiveQuirks:
        """The device's quirks: shipped sets, then the user's, with both off lists."""
        if self.device is None:
            raise RuntimeError("service not started")
        identity = self.device.identity
        sets = list(self._quirk_sets)
        if any(user.items.values()):
            if not identity.manufacturer:
                raise QuirkError("the device has no Model 1 manufacturer to match user quirks to")
            user_set = user.quirk_set(self.device_id, identity.manufacturer)
            if user_set is not None:
                sets.append(user_set)
        check_unique(sets)
        known = {item.id for s in sets for item in s.items}
        for item_id in user.off:
            if item_id not in known:
                _LOGGER.warning("User switched off %s, but no quirk has that id now", item_id)
        off = [*self._quirks_off, *(i for i in user.off if i in known)]
        built = ActiveQuirks(sets, identity, off)
        if self.quirks is not None:
            # Keep each rule's remembered flag across a rebuild.
            built.engine.latched.update(self.quirks.engine.latched)
        return built

    def _need_store(self) -> UserQuirkStore:
        if self.user_store is None:
            raise UserQuirksOff("user quirks are off: the bridge was started without --user-quirks")
        if self.poller is None:
            raise RuntimeError("service not started")
        return self.user_store

    async def check_user_item(
        self, kind: str, item: Any
    ) -> tuple[UserQuirks, ActiveQuirks, dict[str, Any]]:
        """Check one user item (U2) and preview it (U3), without saving anything."""
        self._need_store()
        check_kind(kind)
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise QuirkError(f"a {kind} must be an object with an id")
        user = self.user.with_item(kind, item)
        trial = self._build(user)
        extra = {}
        if kind == "reading":
            [reading] = [r for r in trial.all_readings if r.id == item["id"]]
            async with self._poll_lock:
                extra = await read_raw(self._unit, [reading])
            if extra[reading.id].error is not None:
                raise QuirkError(f"test read of {reading.id} failed: {extra[reading.id].error}")
        assert self.poller is not None
        after = self.poller.preview(trial, extra)
        if item["id"] in trial.failing:
            raise QuirkError(f"{kind} {item['id']}: {trial.failing[item['id']]}")
        preview = {
            "kind": kind,
            "id": item["id"],
            "changes": _diff(self.poller.snapshot, after),
        }
        if kind == "reading":
            preview["test_read"] = json_value(extra[item["id"]].value)
        return user, trial, preview

    async def save_user_item(self, kind: str, item: Any) -> dict[str, Any]:
        """Check, save and activate a user item (U1–U4); it is used from the next poll."""
        async with self._edit_lock:
            user, trial, preview = await self.check_user_item(kind, item)
            self._activate(user, trial)
            _LOGGER.info("User %s %s saved: %s", kind, item["id"], item.get("reason"))
            return preview

    async def remove_user_item(self, kind: str, item_id: str) -> None:
        """Remove a user item (U7); its points fall back to the layer below."""
        async with self._edit_lock:
            self._need_store()
            check_kind(kind)
            if self.user.find(kind, item_id) is None:
                raise KeyError(item_id)
            user = self.user.without_item(kind, item_id)
            self._activate(user, self._build(user))
            _LOGGER.info("User %s %s removed", kind, item_id)

    async def switch_off(self, item_id: str, off: bool) -> None:
        """Switch any item, shipped or the user's, off or back on (U6)."""
        async with self._edit_lock:
            self._need_store()
            assert self.quirks is not None
            if not off and item_id in self._quirks_off:
                raise QuirkError(f"{item_id} is switched off on the command line (--quirk-off)")
            check_off(self.quirks.sets + self.quirks.not_matched, [item_id])
            user = self.user.with_off(item_id, off)
            self._activate(user, self._build(user))
            _LOGGER.info("User switched %s %s", item_id, "off" if off else "on")

    def _activate(self, user: UserQuirks, quirks: ActiveQuirks) -> None:
        """Save first, then use: a failed save changes nothing."""
        self._need_store().save(user)
        self.user = user
        self.quirks = quirks
        assert self.poller is not None
        self.poller.quirks = quirks

    def user_json(self) -> dict[str, Any]:
        return {
            "device": self.device_id,
            "enabled": self.user_store is not None,
            "kinds": list(KINDS),
            "items": self.user.items,
            "off": self.user.off,
        }

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
