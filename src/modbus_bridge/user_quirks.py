"""The user's own quirks for one device (design L5, 2b), kept in one file.

The file holds the user's items in the quirk-set format (point quirks, readings,
constants and rules) and the ids the user has switched off, shipped or their own.
It is written whole to a new file that then replaces the old one, so a crash
never leaves half a file.

Every change is also added to an audit log next to it (U5, U8), one JSON object
per line. A save keeps the item before and after, so each version stays in the log.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .quirks import FORMAT as SET_FORMAT
from .quirks import USER_LAYER, QuirkError, QuirkSet
from .quirks import VERSION as SET_VERSION

FORMAT = "modbus-bridge/user-quirks"
VERSION = 1
#: API kind name to the quirk-set field that holds that kind.
KINDS = {"quirk": "quirks", "reading": "readings", "constant": "constants", "rule": "rules"}
SOURCE = "user quirk"
#: What an audit entry records: a user item saved or removed, any item off or on.
ACTIONS = ("save", "remove", "off", "on")
_ENTRY_FIELDS = {"time", "who", "device", "action", "kind", "id", "version", "before",
                 "after", "reason"}  # fmt: skip


@dataclass
class UserQuirks:
    """The user's items by kind (as JSON objects) and the ids switched off."""

    items: dict[str, list[dict[str, Any]]] = field(
        default_factory=lambda: {k: [] for k in KINDS.values()}
    )
    off: list[str] = field(default_factory=list)

    def to_json(self, device_id: str) -> dict[str, Any]:
        return {
            "format": FORMAT,
            "version": VERSION,
            "device": device_id,
            "items": self.items,
            "off": self.off,
        }

    def find(self, kind: str, item_id: str) -> int | None:
        for index, item in enumerate(self.items[KINDS[kind]]):
            if item.get("id") == item_id:
                return index
        return None

    def with_item(self, kind: str, item: dict[str, Any]) -> UserQuirks:
        """A copy with ``item`` added, or replacing the item of the same id."""
        items = {k: list(v) for k, v in self.items.items()}
        index = self.find(kind, item["id"])
        if index is None:
            items[KINDS[kind]].append(item)
        else:
            items[KINDS[kind]][index] = item
        return UserQuirks(items, list(self.off))

    def without_item(self, kind: str, item_id: str) -> UserQuirks:
        items = {k: [i for i in v if not (k == KINDS[kind] and i.get("id") == item_id)]
                 for k, v in self.items.items()}  # fmt: skip
        return UserQuirks(items, [i for i in self.off if i != item_id])

    def with_off(self, item_id: str, off: bool) -> UserQuirks:
        ids = [i for i in self.off if i != item_id] + ([item_id] if off else [])
        return UserQuirks({k: list(v) for k, v in self.items.items()}, ids)

    def quirk_set(self, device_id: str, manufacturer: str) -> QuirkSet | None:
        """The items as a quirk set at the user layer, or ``None`` if there are none."""
        if not any(self.items.values()):
            return None
        return QuirkSet.from_json(
            {
                "format": SET_FORMAT,
                "version": SET_VERSION,
                "id": f"user-{device_id}",
                "layer": USER_LAYER,
                "match": {"manufacturer": manufacturer},
                "source": SOURCE,
                **{k: v for k, v in self.items.items() if v},
            },
            path=f"user quirks of {device_id}",
        )


def check_kind(kind: str) -> None:
    if kind not in KINDS:
        raise QuirkError(f"kind must be one of {', '.join(KINDS)}, not {kind!r}")


class UserQuirkStore:
    """Where one device's user quirks are kept: ``<directory>/<device-id>.json``."""

    def __init__(self, directory: Path, device_id: str) -> None:
        self.path = Path(directory) / f"{device_id}.json"
        self.device_id = device_id
        self.audit = AuditLog(Path(directory) / f"{device_id}.audit.jsonl", device_id)

    def load(self) -> UserQuirks:
        """The saved user quirks; none if the file does not exist yet."""
        if not self.path.exists():
            return UserQuirks()
        try:
            data = json.loads(self.path.read_text())
        except (OSError, ValueError) as err:
            raise QuirkError(f"{self.path}: {err}") from err
        if not isinstance(data, dict) or data.get("format") != FORMAT:
            raise QuirkError(f"{self.path}: format must be {FORMAT!r}")
        if data.get("version") != VERSION:
            raise QuirkError(f"{self.path}: version must be {VERSION}")
        if data.get("device") != self.device_id:
            raise QuirkError(f"{self.path}: it is for device {data.get('device')!r}")
        items = data.get("items")
        off = data.get("off")
        if not isinstance(items, dict) or set(items) - set(KINDS.values()):
            raise QuirkError(f"{self.path}: items must hold {', '.join(KINDS.values())}")
        if not all(isinstance(v, list) for v in items.values()):
            raise QuirkError(f"{self.path}: each kind of item must be a list")
        if not isinstance(off, list) or not all(isinstance(i, str) for i in off):
            raise QuirkError(f"{self.path}: off must be a list of ids")
        return UserQuirks({k: list(items.get(k, [])) for k in KINDS.values()}, list(off))

    def save(self, quirks: UserQuirks) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        new = self.path.with_suffix(".json.new")
        with new.open("w") as file:
            json.dump(quirks.to_json(self.device_id), file, indent=2, ensure_ascii=False)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())
        new.replace(self.path)


class AuditLog:
    """Every change to one device's user quirks, oldest first (design U5, U8).

    Entries are only ever added. Each save of an item is a new version of it:
    1, 2, 3 and so on, carrying on after a remove and a later save.
    """

    def __init__(self, path: Path, device_id: str) -> None:
        self.path = path
        self.device_id = device_id
        self._versions: dict[tuple[str, str], int] = {}

    def load(self) -> None:
        """Read the log to learn each item's last version; a broken line is an error."""
        self._versions = {}
        for entry in self.entries():
            if entry["action"] == "save":
                self._versions[entry["kind"], entry["id"]] = entry["version"]

    def entries(self, item_id: str | None = None) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            lines = self.path.read_text().splitlines()
        except OSError as err:
            raise QuirkError(f"{self.path}: {err}") from err
        entries = []
        for number, line in enumerate(lines, 1):
            try:
                entry = json.loads(line)
            except ValueError as err:
                raise QuirkError(f"{self.path}: line {number}: {err}") from err
            if (
                not isinstance(entry, dict)
                or set(entry) != _ENTRY_FIELDS
                or entry["action"] not in ACTIONS
                or not isinstance(entry["id"], str)
                or (entry["action"] == "save" and not isinstance(entry["version"], int))
            ):
                raise QuirkError(f"{self.path}: line {number}: not an audit entry")
            if item_id is None or entry["id"] == item_id:
                entries.append(entry)
        return entries

    def next_version(self, kind: str, item_id: str) -> int:
        return self._versions.get((kind, item_id), 0) + 1

    def add(
        self,
        who: str,
        action: str,
        item_id: str,
        *,
        kind: str | None = None,
        before: Any = None,
        after: Any = None,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """Add one entry and wait until it is on disk."""
        version = self.next_version(kind, item_id) if action == "save" and kind else None
        entry = {
            "time": datetime.now(UTC).isoformat(timespec="seconds"),
            "who": who,
            "device": self.device_id,
            "action": action,
            "kind": kind,
            "id": item_id,
            "version": version,
            "before": before,
            "after": after,
            "reason": reason,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a") as file:
            file.write(json.dumps(entry, ensure_ascii=False) + "\n")
            file.flush()
            os.fsync(file.fileno())
        if version is not None and kind is not None:
            self._versions[kind, item_id] = version
        return entry
