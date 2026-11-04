"""Quirk sets: corrections to SunSpec points, held as data (design L2–L4, rule 9).

A quirk-set file names one layer (vendor, model or firmware), the Model 1 values
it matches, its source, and its quirks. Each quirk changes one point (or a
pattern of points): scale, invert, units, label or hide. Higher layers override
lower ones change by change. Every quirk can be switched off by its id; the point
then falls back to the layer below. A quirk that cannot be applied gives no
value, never a guess (rule 8, design U9).
"""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .raw import RawReading, RawReadingError, RawResult, by_name, parse_reading

if TYPE_CHECKING:
    from .poller import PointState
    from .sunspec import DeviceIdentity

_LOGGER = logging.getLogger(__name__)

FORMAT = "modbus-bridge/quirk-set"
VERSION = 1
#: Layers in the order they apply, lowest first (design L2–L4).
LAYERS = ("vendor", "model", "firmware")
CHANGES = ("scale", "invert", "units", "label", "hide")

_MATCH_FIELDS = {
    "vendor": ({"manufacturer"}, set()),
    "model": ({"manufacturer", "model"}, {"options"}),
    "firmware": ({"manufacturer", "firmware"}, {"model"}),
}
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
_KEY = re.compile(r"^(\d+(#\d+)?|raw)(\.[A-Za-z_][A-Za-z0-9_]*(\[(\d+|\*)\])?)+$")


class QuirkError(ValueError):
    """A quirk-set file, or the options that use it, are not valid."""


def version_numbers(text: str | None) -> tuple[int, ...] | None:
    """``V12R02B60D00`` gives ``(12, 2, 60, 0)``; text without numbers gives ``None``."""
    numbers = tuple(int(n) for n in re.findall(r"\d+", text or ""))
    return numbers or None


@dataclass(frozen=True)
class Match:
    """The Model 1 values a quirk set applies to."""

    manufacturer: str
    models: tuple[str, ...] | None = None
    options: tuple[str, ...] | None = None
    firmware_min: tuple[int, ...] | None = None
    firmware_max: tuple[int, ...] | None = None
    text: Mapping[str, Any] = field(default_factory=dict)

    def accepts(self, identity: DeviceIdentity) -> bool:
        if identity.manufacturer != self.manufacturer:
            return False
        if self.models is not None and identity.model not in self.models:
            return False
        if self.options is not None and identity.options not in self.options:
            return False
        if self.firmware_min is None and self.firmware_max is None:
            return True
        version = version_numbers(identity.version)
        if version is None:
            return False
        if self.firmware_min is not None and version < self.firmware_min:
            return False
        return not (self.firmware_max is not None and version > self.firmware_max)


@dataclass(frozen=True)
class Quirk:
    """One correction to one point or pattern of points."""

    id: str
    point: str
    reason: str
    source: str
    layer: str
    set_id: str
    changes: Mapping[str, Any]
    _pattern: re.Pattern[str] = field(repr=False, compare=False, default=re.compile(""))

    def matches(self, key: str) -> bool:
        if self._pattern.fullmatch(key):
            return True
        if "#" in self.point.split(".", 1)[0]:
            return False
        return bool(self._pattern.fullmatch(re.sub(r"^(\d+)#\d+", r"\1", key)))


@dataclass(frozen=True)
class QuirkSet:
    """One quirk-set file."""

    id: str
    layer: str
    match: Match
    source: str
    quirks: tuple[Quirk, ...]
    path: str
    readings: tuple[RawReading, ...] = ()

    @classmethod
    def load(cls, path: Path) -> QuirkSet:
        try:
            data = json.loads(Path(path).read_text())
            return cls.from_json(data, str(path))
        except (OSError, json.JSONDecodeError) as err:
            raise QuirkError(f"{path}: {err}") from err
        except QuirkError as err:
            raise QuirkError(f"{path}: {err}") from err

    @classmethod
    def from_json(cls, data: Any, path: str = "<data>") -> QuirkSet:
        _object(data, "quirk set", {"format", "version", "id", "layer", "match", "source"},
                {"quirks", "readings", "description"})  # fmt: skip
        if data["format"] != FORMAT or data["version"] != VERSION:
            raise QuirkError(f"format must be {FORMAT!r} version {VERSION}")
        set_id = _id(data["id"], "set id")
        layer = data["layer"]
        if layer not in LAYERS:
            raise QuirkError(f"layer must be one of {', '.join(LAYERS)}, not {layer!r}")
        source = _text(data["source"], "source")
        match = _match(layer, data["match"])
        quirks = tuple(_quirk(q, layer, set_id, source) for q in data.get("quirks", []))
        try:
            readings = tuple(
                parse_reading(r, layer, set_id, source) for r in data.get("readings", [])
            )
        except RawReadingError as err:
            raise QuirkError(str(err)) from err
        for name, same in by_name(readings).items():
            if len(same) > 1:
                raise QuirkError(f"reading name {name!r} is used twice in one set")
        return cls(set_id, layer, match, source, quirks, path, readings)


def _object(data: Any, what: str, required: set[str], optional: set[str]) -> None:
    if not isinstance(data, dict):
        raise QuirkError(f"{what} must be an object")
    missing = required - data.keys()
    unknown = data.keys() - required - optional
    if missing:
        raise QuirkError(f"{what} is missing {', '.join(sorted(missing))}")
    if unknown:
        raise QuirkError(f"{what} has unknown field(s) {', '.join(sorted(unknown))}")


def _text(value: Any, what: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise QuirkError(f"{what} must be non-empty text")
    return value


def _id(value: Any, what: str) -> str:
    if not isinstance(value, str) or not _ID.match(value):
        raise QuirkError(f"{what} {value!r} must be letters, digits, '.', '_' or '-'")
    return value


def _texts(value: Any, what: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise QuirkError(f"{what} must be a non-empty list")
    return tuple(_text(v, what) for v in value)


def _match(layer: str, data: Any) -> Match:
    required, optional = _MATCH_FIELDS[layer]
    _object(data, f"{layer} match", required, optional)
    firmware_min = firmware_max = None
    if "firmware" in data:
        firmware = data["firmware"]
        _object(firmware, "firmware match", set(), {"min", "max"})
        if not firmware:
            raise QuirkError("firmware match needs min, max or both")
        if "min" in firmware:
            firmware_min = version_numbers(_text(firmware["min"], "firmware min"))
        if "max" in firmware:
            firmware_max = version_numbers(_text(firmware["max"], "firmware max"))
        if (firmware_min is None and "min" in firmware) or (
            firmware_max is None and "max" in firmware
        ):
            raise QuirkError("firmware min and max must contain numbers")
    return Match(
        manufacturer=_text(data["manufacturer"], "manufacturer"),
        models=_texts(data["model"], "model") if "model" in data else None,
        options=_texts(data["options"], "options") if "options" in data else None,
        firmware_min=firmware_min,
        firmware_max=firmware_max,
        text=data,
    )


def _pattern(point: str) -> re.Pattern[str]:
    return re.compile(re.escape(point).replace(r"\[\*\]", r"\[\d+\]"))


def _quirk(data: Any, layer: str, set_id: str, source: str) -> Quirk:
    _object(data, "quirk", {"id", "point", "reason"}, {"source", *CHANGES})
    quirk_id = _id(data["id"], "quirk id")
    point = data["point"]
    if not isinstance(point, str) or not _KEY.match(point):
        raise QuirkError(f"quirk {quirk_id}: point {point!r} is not a point key")
    changes = {name: data[name] for name in CHANGES if name in data}
    if not changes:
        raise QuirkError(f"quirk {quirk_id}: no change given")
    if "hide" in changes and len(changes) > 1:
        raise QuirkError(f"quirk {quirk_id}: hide cannot be combined with other changes")
    for name in ("invert", "hide"):
        if name in changes and not isinstance(changes[name], bool):
            raise QuirkError(f"quirk {quirk_id}: {name} must be true or false")
    if "scale" in changes:
        scale = changes["scale"]
        if isinstance(scale, bool) or not isinstance(scale, (int, float)) or scale == 0:
            raise QuirkError(f"quirk {quirk_id}: scale must be a non-zero number")
    for name in ("units", "label"):
        if name in changes:
            _text(changes[name], f"quirk {quirk_id} {name}")
    return Quirk(
        id=quirk_id,
        point=point,
        reason=_text(data["reason"], f"quirk {quirk_id} reason"),
        source=_text(data.get("source", source), f"quirk {quirk_id} source"),
        layer=layer,
        set_id=set_id,
        changes=changes,
        _pattern=_pattern(point),
    )


def load_sets(paths: Iterable[Path]) -> list[QuirkSet]:
    """Load quirk-set files; a directory loads its ``*.json`` files in name order.

    Duplicate set ids, and quirk or reading ids used twice anywhere, are refused.
    """
    files: list[Path] = []
    for path in paths:
        path = Path(path)
        files += sorted(path.glob("*.json")) if path.is_dir() else [path]
    sets = [QuirkSet.load(f) for f in files]
    seen_sets: set[str] = set()
    seen_quirks: set[str] = set()
    for quirk_set in sets:
        if quirk_set.id in seen_sets:
            raise QuirkError(f"{quirk_set.path}: set id {quirk_set.id!r} is used twice")
        seen_sets.add(quirk_set.id)
        for item in (*quirk_set.quirks, *quirk_set.readings):
            if item.id in seen_quirks:
                raise QuirkError(f"{quirk_set.path}: quirk id {item.id!r} is used twice")
            seen_quirks.add(item.id)
    return sets


@dataclass
class _Effect:
    changes: dict[str, Quirk]
    clashes: dict[str, str]


class ActiveQuirks:
    """The quirks that apply to one device, chosen by its Model 1."""

    def __init__(
        self,
        sets: Sequence[QuirkSet],
        identity: DeviceIdentity,
        disabled: Iterable[str] = (),
    ) -> None:
        self.disabled = frozenset(disabled)
        known = {q.id for s in sets for q in (*s.quirks, *s.readings)}
        unknown = self.disabled - known
        if unknown:
            raise QuirkError(f"cannot switch off unknown quirk id(s) {', '.join(sorted(unknown))}")
        matched = [s for s in sets if s.match.accepts(identity)]
        self.sets = sorted(matched, key=lambda s: LAYERS.index(s.layer))
        self.not_matched = [s for s in sets if s not in matched]
        self.quirks = [q for s in self.sets for q in s.quirks]
        self.failing: dict[str, str] = {}
        self.used: set[str] = set()
        """Quirks whose pattern matched a point."""
        self.effective: set[str] = set()
        """Quirks that supply at least one change to a point (not wholly overridden)."""
        self._effects: dict[str, _Effect] = {}
        self.all_readings = [r for s in self.sets for r in s.readings]
        self.readings: list[RawReading] = []
        """The reading used for each name: the highest layer that is not switched off."""
        self.reading_clashes: dict[str, list[RawReading]] = {}
        """Names with two readings in their top layer; their points have no value."""
        self.read_errors: dict[str, str] = {}
        """The last read error of each reading, cleared when it reads again."""
        switched_on = [r for r in self.all_readings if r.id not in self.disabled]
        for name, same in by_name(switched_on).items():
            top = [r for r in same if r.layer == same[-1].layer]
            if len(top) > 1:
                self.reading_clashes[name] = top
                for reading in top:
                    others = ", ".join(r.id for r in top if r is not reading)
                    self._fail(reading.id, f"clashes with {others} on raw.{name} (same layer)")
            else:
                self.readings.append(top[0])
        for quirk_set in self.sets:
            _LOGGER.info(
                "Quirk set %s (%s layer) applies; source: %s",
                quirk_set.id, quirk_set.layer, quirk_set.source,
            )  # fmt: skip
        for quirk in self.quirks:
            state = "switched off" if quirk.id in self.disabled else "active"
            _LOGGER.info(
                "Quirk %s on %s %s: %s (%s); source: %s",
                quirk.id, quirk.point, state, _describe(quirk.changes), quirk.reason, quirk.source,
            )  # fmt: skip
        for reading in self.all_readings:
            state = "switched off" if reading.id in self.disabled else "active"
            _LOGGER.info(
                "Reading %s (%s) %s: %s %s at %d (%s); source: %s",
                reading.id, reading.key, state, reading.table, reading.type, reading.address,
                reading.reason, reading.source,
            )  # fmt: skip
        for quirk_set in self.not_matched:
            _LOGGER.info("Quirk set %s does not match this device", quirk_set.id)

    def _effect(self, key: str) -> _Effect:
        effect = self._effects.get(key)
        if effect is not None:
            return effect
        effect = _Effect({}, {})
        for quirk in self.quirks:
            if quirk.id in self.disabled or not quirk.matches(key):
                continue
            self.used.add(quirk.id)
            for name in quirk.changes:
                earlier = effect.changes.get(name)
                if earlier is not None and earlier.layer == quirk.layer:
                    error = f"clashes with {earlier.id} on {key} ({name}, same layer)"
                    effect.clashes[quirk.id] = error
                    effect.clashes[earlier.id] = f"clashes with {quirk.id} on {key} ({name})"
                effect.changes[name] = quirk
        self.effective.update(q.id for q in effect.changes.values())
        self._effects[key] = effect
        return effect

    def _fail(self, quirk_id: str, error: str) -> None:
        if quirk_id not in self.failing:
            self.failing[quirk_id] = error
            _LOGGER.error("Quirk %s failing: %s", quirk_id, error)

    def apply(self, state: PointState) -> PointState | None:
        """The point after its quirks, or ``None`` if a quirk hides it."""
        effect = self._effect(state.key)
        if not effect.changes:
            return state

        def change(name: str, default: Any = None) -> Any:
            quirk = effect.changes.get(name)
            return default if quirk is None else quirk.changes[name]

        if change("hide", False):
            return None
        value = state.value
        for quirk_id, error in effect.clashes.items():
            self._fail(quirk_id, error)
        if effect.clashes:
            value = None
        value_quirks = [effect.changes[n] for n in ("scale", "invert") if n in effect.changes]
        if value is not None and value_quirks:
            if isinstance(value, (bool, Enum)) or not isinstance(value, (int, float)):
                for quirk in value_quirks:
                    self._fail(quirk.id, f"{state.key} is not a number ({type(value).__name__})")
                value = None
            else:
                value = round(value * change("scale", 1), 9)
                if change("invert", False):
                    value = -value
        return replace(
            state,
            value=value,
            units=change("units", state.units),
            label=change("label", state.label),
            quirks=tuple(sorted({*state.quirks, *(q.id for q in effect.changes.values())})),
        )

    def state_of(self, quirk: Quirk) -> str:
        if quirk.id in self.disabled:
            return "off"
        if quirk.id in self.failing:
            return "failing"
        if quirk.id in self.effective:
            return "active"
        if quirk.id in self.used:
            return "overridden"  # every change it makes is replaced by a higher layer
        return "unused"

    def raw_states(self, results: Mapping[str, RawResult]) -> list[PointState]:
        """Point states for the readings in use, before point quirks."""
        from .poller import PointState

        for reading in self.readings:
            result = results.get(reading.id)
            error = None if result is None else result.error
            if error is None:
                self.read_errors.pop(reading.id, None)
            elif self.read_errors.get(reading.id) != error:
                self.read_errors[reading.id] = error
                _LOGGER.warning("Reading %s not read: %s", reading.id, error)
        states = [
            PointState(
                key=reading.key,
                name=reading.name,
                label=reading.label,
                units=reading.units,
                writable=False,
                value=None if reading.id not in results else results[reading.id].value,
                sunspec_type=reading.type,
                quirks=(reading.id,),
            )
            for reading in self.readings
        ]
        for name, same in self.reading_clashes.items():
            first = same[0]
            states.append(
                PointState(
                    f"raw.{name}",
                    name,
                    first.label,
                    first.units,
                    False,
                    None,
                    first.type,
                    tuple(r.id for r in same),
                )  # fmt: skip
            )
        return states

    def reading_state(self, reading: RawReading) -> str:
        if reading.id in self.disabled:
            return "off"
        if reading.id in self.failing or reading.id in self.read_errors:
            return "failing"
        if reading in self.readings:
            return "active"
        return "overridden"

    def report(self) -> dict[str, Any]:
        """Every quirk of the matching sets with its state, for the API."""
        return {
            "sets": [
                {"id": s.id, "layer": s.layer, "match": dict(s.match.text), "source": s.source}
                for s in self.sets
            ],
            "quirks": [
                {
                    "id": q.id,
                    "set": q.set_id,
                    "layer": q.layer,
                    "point": q.point,
                    "changes": dict(q.changes),
                    "reason": q.reason,
                    "source": q.source,
                    "state": self.state_of(q),
                    "error": self.failing.get(q.id),
                }
                for q in self.quirks
            ],
            "readings": [
                {
                    **r.describe(),
                    "state": self.reading_state(r),
                    "error": self.failing.get(r.id) or self.read_errors.get(r.id),
                }
                for r in self.all_readings
            ],
            "not_matched": [s.id for s in self.not_matched],
        }


def _describe(changes: Mapping[str, Any]) -> str:
    return ", ".join(f"{name}={value!r}" for name, value in changes.items())
