"""One device kept up to date in the background, with change subscribers (design D9).

The service owns the poller for one unit. The caller owns the Modbus connection
(rule 7: one connection per device), so tests can pass a mock unit.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from enum import Enum, Flag
from typing import Any

from modbus_connection import ModbusError, ModbusUnit
from modbus_connection.model.sunspec import SunSpecError

from .implemented import ImplementedPoints, discover_implemented
from .pics import PicsProfile, apply_pics
from .poller import PointState, Poller
from .quirks import FORMAT as SET_FORMAT
from .quirks import VERSION as SET_VERSION
from .quirks import ActiveQuirks, QuirkError, QuirkSet, check_off, check_unique
from .raw import read_raw
from .sunspec import DeviceIdentity, SunSpecDevice, discover
from .user_quirks import KINDS, SOURCE, AuditLog, UserQuirks, UserQuirkStore, check_kind

_LOGGER = logging.getLogger(__name__)

#: What a subscriber receives per poll: sequence, changed points, removed keys.
Update = tuple[int, list[PointState], list[str]]
#: Changes a slow subscriber may fall behind by before it is dropped. A dropped
#: subscriber reconnects and starts again from a snapshot.
QUEUE_SIZE = 2000
PROPOSAL_FORMAT = "modbus-bridge/quirk-proposal"
PROPOSAL_VERSION = 1
#: The audit fields a proposal keeps; who made a change and the device id stay out.
_HISTORY_FIELDS = ("time", "action", "version", "before", "after", "reason")


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


class AuditError(RuntimeError):
    """A change could not be added to the audit log, so it was not made."""


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


def _number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _warnings(changes: Sequence[Mapping[str, Any]]) -> list[str]:
    """What HA users should know first: a point that stays but changes unit or scale (Q4).

    The before and after states come from the same poll's data, so a number that
    differs under the same unit was rescaled or recalculated by the change.
    """
    warnings = []
    for change in changes:
        old, new = change["before"], change["after"]
        if old is None or new is None:
            continue
        if old["units"] != new["units"]:
            what = f"unit {old['units']} → {new['units']}"
        elif _number(old["value"]) and _number(new["value"]) and old["value"] != new["value"]:
            what = f"value {old['value']} → {new['value']} with the same unit {old['units']}"
        else:
            continue
        warnings.append(
            f"{change['key']}: {what}. Home Assistant's history and long-term statistics "
            "for this entity will mix old and new values; HA may raise a repair notice."
        )
    return warnings


def _who(identity: DeviceIdentity) -> tuple[str | None, str | None, str | None]:
    """What makes a device the same device: maker, model and serial."""
    return identity.manufacturer, identity.model, identity.serial


def _describe(identity: DeviceIdentity) -> str:
    return " ".join(str(x) for x in _who(identity) if x) or "no Model 1 identity"


def _layout(device: SunSpecDevice) -> tuple[Any, ...]:
    return device.base_address, tuple((m.model_id, m.address, m.length) for m in device.chain)


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
        self._subscribers: set[asyncio.Queue[Update | None]] = set()
        self._task: asyncio.Task[None] | None = None
        self._recheck = False
        """Set when the link may have been rebuilt: check the device before the next poll."""
        self._check_failing = False
        """The last check could not read the device (its warning was logged)."""
        self.refused: str | None = None
        """Why another device at this address is not read, once one was found."""
        self._unsubscribe_lost: Callable[[], None] | None = None

    @property
    def interval(self) -> float:
        """Seconds between polls."""
        return self._interval

    @property
    def implemented(self) -> ImplementedPoints:
        if self.poller is None:
            raise RuntimeError("service not started")
        return self.poller.implemented

    async def setup(self) -> None:
        """Discover the device and its implemented points, then poll once."""
        self.device = await discover(self._unit)
        if not self.device.identity.serial:
            _LOGGER.warning(
                "Device %s has no Model 1 serial: after a reconnect, another device of the "
                "same model at this address cannot be told apart", self.device_id,
            )  # fmt: skip
        if self.user_store is not None:
            self.user = self.user_store.load()
            self.user_store.audit.load()
        self.quirks = self._build(self.user)
        implemented = await self._implemented(self.device)
        self.poller = Poller(self._unit, self.device.chain, implemented, self.quirks)
        self._unsubscribe_lost = self._unit.on_connection_lost(self._connection_lost)
        await self.poll_once()

    async def _implemented(self, device: SunSpecDevice) -> ImplementedPoints:
        implemented, _ = await discover_implemented(
            self._unit, device.chain, self._reads, self._read_interval
        )
        if self._profile is not None:
            implemented, _ = apply_pics(implemented, self._profile)
        return implemented

    def _connection_lost(self) -> None:
        self._recheck = True

    async def poll_once(self) -> list[PointState]:
        if self.poller is None:
            raise RuntimeError("service not started")
        problem = None
        if self._recheck and self.refused is None:
            # Edit lock first, as an edit takes it before the poll lock.
            async with self._edit_lock, self._poll_lock:
                problem = await self._recheck_device()
        async with self._poll_lock:
            if self.refused is not None:
                changes = self.poller.fail(self.refused)
            elif problem is not None:
                changes = self.poller.fail(problem)
            else:
                changes = await self.poller.poll()
                if self.poller.last_error is not None:
                    self._recheck = True  # the link may have gone; check before trusting it
            removed = list(self.poller.removed)
        if changes or removed:
            self.sequence += 1
            self._publish(self.sequence, changes, removed)
        return changes

    async def _recheck_device(self) -> str | None:
        """Read SunSpec and Model 1 again after a reconnect (design Q3, rule 8).

        Returns why the device could not be checked, or ``None``. Refuses another
        device; sets the same device up again if its firmware, options or chain changed.
        """
        assert self.device is not None and self.poller is not None
        try:
            found = await discover(self._unit)
        except (ModbusError, SunSpecError) as err:
            problem = f"not checked after a reconnect: {type(err).__name__}: {err}"
            # Once per outage at WARNING; the retries at every poll only at DEBUG.
            level = logging.DEBUG if self._check_failing else logging.WARNING
            _LOGGER.log(level, "Device %s %s; all points unavailable", self.device_id, problem)
            self._check_failing = True
            return problem
        self._recheck = False
        self._check_failing = False
        old, new = self.device.identity, found.identity
        if _who(old) != _who(new):
            self.refused = (
                f"another device answers at this address: it reports {_describe(new)}, "
                f"but this bridge was started for {_describe(old)}. "
                "It is not read again until the bridge is restarted"
            )
            _LOGGER.error("Device %s refused: %s", self.device_id, self.refused)
            return None
        chain_changed = _layout(found) != _layout(self.device)
        if old == new and not chain_changed:
            _LOGGER.info("Device %s checked after a reconnect: unchanged", self.device_id)
            return None
        _LOGGER.warning(
            "Device %s changed after a reconnect: firmware %s -> %s, options %s -> %s%s; "
            "quirks rebuilt", self.device_id, old.version, new.version, old.options,
            new.options, ", model chain changed" if chain_changed else "",
        )  # fmt: skip
        self.device = found
        self.quirks = self._build(self.user)
        self.poller.quirks = self.quirks
        if chain_changed:
            self.poller.rebind(found.chain, await self._implemented(found))
        return None

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
        # Both sides from the same poll's data: the snapshot may predate the last edit.
        assert self.quirks is not None
        changes = _diff(self.poller.preview(self.quirks, extra), after)
        preview = {
            "kind": kind,
            "id": item["id"],
            "changes": changes,
            "warnings": _warnings(changes),
        }
        if kind == "reading":
            preview["test_read"] = json_value(extra[item["id"]].value)
        return user, trial, preview

    def _item(self, kind: str, item_id: str) -> dict[str, Any] | None:
        index = self.user.find(kind, item_id)
        return None if index is None else self.user.items[KINDS[kind]][index]

    async def save_user_item(self, kind: str, item: Any, who: str) -> dict[str, Any]:
        """Check, save and activate a user item (U1–U5); it is used from the next poll."""
        async with self._edit_lock:
            user, trial, preview = await self.check_user_item(kind, item)
            before = self._item(kind, item["id"])
            entry = self._activate(user, trial, lambda log: log.add(
                who, "save", item["id"], kind=kind, before=before, after=item,
                reason=item.get("reason"),
            ))  # fmt: skip
            _LOGGER.info("User %s %s saved as version %s by %s: %s",
                         kind, item["id"], entry["version"], who, item.get("reason"))  # fmt: skip
            return {**preview, "version": entry["version"]}

    async def remove_user_item(
        self, kind: str, item_id: str, who: str, reason: str | None = None
    ) -> list[str]:
        """Remove a user item (U7); its points fall back to the layer below.

        Returns the warnings for points that change unit or scale (Q4)."""
        async with self._edit_lock:
            self._need_store()
            check_kind(kind)
            before = self._item(kind, item_id)
            if before is None:
                raise KeyError(item_id)
            user = self.user.without_item(kind, item_id)
            quirks = self._build(user)
            warnings = self._warnings_for(quirks)
            self._activate(user, quirks, lambda log: log.add(
                who, "remove", item_id, kind=kind, before=before, reason=reason,
            ))  # fmt: skip
            _LOGGER.info("User %s %s removed by %s: %s", kind, item_id, who, reason)
            return warnings

    async def switch_off(
        self, item_id: str, off: bool, who: str, reason: str | None = None
    ) -> list[str]:
        """Switch any item, shipped or the user's, off or back on (U6).

        Returns the warnings for points that change unit or scale (Q4)."""
        async with self._edit_lock:
            self._need_store()
            assert self.quirks is not None
            if not off and item_id in self._quirks_off:
                raise QuirkError(f"{item_id} is switched off on the command line (--quirk-off)")
            check_off(self.quirks.sets + self.quirks.not_matched, [item_id])
            before = item_id in self.user.off
            user = self.user.with_off(item_id, off)
            action = "off" if off else "on"
            quirks = self._build(user)
            warnings = self._warnings_for(quirks)
            self._activate(user, quirks, lambda log: log.add(
                who, action, item_id, before=before, after=off, reason=reason,
            ))  # fmt: skip
            _LOGGER.info("User switched %s %s by %s: %s", item_id, action, who, reason)
            return warnings

    def _warnings_for(self, quirks: ActiveQuirks) -> list[str]:
        assert self.poller is not None
        assert self.quirks is not None
        before = self.poller.preview(self.quirks)
        return _warnings(_diff(before, self.poller.preview(quirks)))

    def _activate(
        self, user: UserQuirks, quirks: ActiveQuirks, record: Callable[[AuditLog], Any]
    ) -> Any:
        """Save, log, then use. If either write fails, nothing changes."""
        store = self._need_store()
        store.save(user)
        try:
            entry = record(store.audit)
        except OSError as err:
            store.save(self.user)  # put the old file back
            message = f"the change was not made: audit log {store.audit.path}: {err}"
            raise AuditError(message) from err
        self.user = user
        self.quirks = quirks
        assert self.poller is not None
        self.poller.quirks = quirks
        return entry

    def audit_json(self, item_id: str | None = None) -> dict[str, Any]:
        """The audit log (U8), oldest first; only ``item_id``'s entries if given."""
        entries = self._need_store().audit.entries(item_id)
        return {"device": self.device_id, "entries": entries}

    def versions_json(self, kind: str, item_id: str) -> dict[str, Any]:
        """Each saved version of one user item (U5), oldest first."""
        entries = self._need_store().audit.entries(item_id)
        versions = [
            {k: e[k] for k in ("version", "time", "who", "reason")} | {"item": e["after"]}
            for e in entries
            if e["action"] == "save" and e["kind"] == kind
        ]
        return {"device": self.device_id, "kind": kind, "id": item_id, "versions": versions}

    def export_json(self, kind: str, item_id: str) -> dict[str, Any]:
        """One user item as a proposal for a shipped quirk (U11), to be shared.

        It holds no serial, device id, host or token. Nothing is saved or logged.
        """
        self._need_store()
        check_kind(kind)
        item = self._item(kind, item_id)
        if item is None:
            raise KeyError(item_id)
        assert self.device is not None and self.poller is not None and self.quirks is not None
        identity = self.device.identity
        if not identity.manufacturer or not identity.model:
            raise QuirkError("the device has no Model 1 manufacturer and model to propose for")
        without = self._build(self.user.without_item(kind, item_id))
        effect = _diff(self.poller.preview(without), self.poller.preview(self.quirks))
        firmware = identity.version or "unknown"
        source = item.get("source") or (
            f"{SOURCE}: own measurement on {identity.manufacturer} {identity.model}, "
            f"firmware {firmware}"
        )
        quirk_set = {
            "format": SET_FORMAT,
            "version": SET_VERSION,
            "id": f"proposal-{item_id}",
            "layer": "model",
            "match": {"manufacturer": identity.manufacturer, "model": [identity.model]},
            "source": source,
            KINDS[kind]: [item],
        }
        QuirkSet.from_json(quirk_set, path=f"proposal for {kind} {item_id}")
        try:
            entries = self._need_store().audit.entries(item_id)
        except QuirkError as err:
            raise AuditError(f"the history cannot be read: {err}") from err
        history = [{k: e[k] for k in _HISTORY_FIELDS} for e in entries if e["kind"] in (kind, None)]
        return {
            "format": PROPOSAL_FORMAT,
            "version": PROPOSAL_VERSION,
            "exported": datetime.now(UTC).isoformat(timespec="seconds"),
            "kind": kind,
            "id": item_id,
            "reason": item.get("reason"),
            "source": item.get("source"),
            "device": {
                "manufacturer": identity.manufacturer,
                "model": identity.model,
                "options": identity.options,
                "firmware": identity.version,
            },
            "switched_off": item_id in self.user.off,
            "effect": effect,
            "history": history,
            "quirk_set": quirk_set,
        }

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
        if self._unsubscribe_lost is not None:
            self._unsubscribe_lost()
            self._unsubscribe_lost = None
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

    def subscribe(self) -> asyncio.Queue[Update | None]:
        queue: asyncio.Queue[Update | None] = asyncio.Queue(QUEUE_SIZE)
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[Any]) -> None:
        self._subscribers.discard(queue)

    def _publish(
        self, sequence: int, changes: Sequence[PointState], removed: Sequence[str] = ()
    ) -> None:
        for queue in list(self._subscribers):
            try:
                queue.put_nowait((sequence, list(changes), list(removed)))
            except asyncio.QueueFull:
                _LOGGER.warning("Dropping a slow subscriber of %s", self.device_id)
                self._close(queue)

    def _close(self, queue: asyncio.Queue[Any]) -> None:
        """End a subscriber's stream; ``None`` tells it to stop."""
        self._subscribers.discard(queue)
        with contextlib.suppress(asyncio.QueueFull):
            queue.put_nowait(None)
