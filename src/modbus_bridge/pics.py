"""PICS profiles: implemented points from a published SunSpec certification (design D6.3).

A profile is a JSON file made from a PICS spreadsheet by ``scripts/convert_pics.py``.
For the models it covers, the PICS decides which points are implemented. Models
it does not cover are sorted by discovery (D6.5). Where the device and the PICS
disagree, it is reported, and a point that gives a value is always implemented
(D6.4).
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .implemented import ImplementedPoints

_LOGGER = logging.getLogger(__name__)

PROFILE_FORMAT = "modbus-bridge/pics-profile"
PROFILE_VERSION = 2
#: Versions that still load. Version 1 has no certified values or Min/Max.
READABLE_VERSIONS = (1, 2)


def pics_path_to_key_path(name: str) -> str:
    """Convert a PICS point name to our point path, without the model prefix.

    ``Crv.1.MustTrip.Pt.1.V`` becomes ``Crv[1].MustTrip[1].Pt[1].V``: a number
    after a group is its 1-based index, and a group without one is ``[1]``.
    """
    parts = name.strip().split(".")
    out: list[str] = []
    index = 0
    while index < len(parts):
        part = parts[index]
        last = index == len(parts) - 1
        if last:
            out.append(part)
            break
        following = parts[index + 1]
        if following.isdigit():
            out.append(f"{part}[{int(following)}]")
            index += 2
        else:
            out.append(f"{part}[1]")
            index += 1
    return ".".join(out)


def _model_id(key: str) -> int:
    """``701#2.W`` gives 701."""
    return int(re.split(r"[.#]", key, maxsplit=1)[0])


def _path(key: str) -> str:
    """``701#2.Crv[1].V`` gives ``Crv[1].V``."""
    return key.split(".", 1)[1]


@dataclass(frozen=True)
class PicsProfile:
    """One PICS, as data."""

    certificate: str
    info: dict[str, Any]
    models: dict[int, dict[str, frozenset[str]]]
    """Model id to ``implemented`` and ``not_implemented`` point paths."""
    details: dict[int, dict[str, dict[str, Any]]] = field(default_factory=dict)
    """Model id to point path to ``value`` (as the test lab recorded it), ``min`` and
    ``max``, each only where the PICS gives one."""

    @classmethod
    def load(cls, path: Path) -> PicsProfile:
        data = json.loads(path.read_text())
        if data.get("format") != PROFILE_FORMAT or data.get("version") not in READABLE_VERSIONS:
            raise ValueError(f"{path}: not a PICS profile of version {READABLE_VERSIONS}")
        models = {
            int(model_id): {
                "implemented": frozenset(entry["implemented"]),
                "not_implemented": frozenset(entry["not_implemented"]),
            }
            for model_id, entry in data["models"].items()
        }
        details = {
            int(model_id): dict(entry.get("details", {}))
            for model_id, entry in data["models"].items()
        }
        info = {k: v for k, v in data.items() if k not in ("models", "format", "version")}
        return cls(certificate=data["certificate"], info=info, models=models, details=details)


def pics_status(profile: PicsProfile | None, key: str) -> str | None:
    """What the PICS says about one point: ``implemented``, ``unimplemented``,
    ``not listed`` (a model the PICS covers, without this point) or ``model not
    covered``. ``None`` with no PICS, or for a point not from a SunSpec model."""
    if profile is None or not re.match(r"^\d+(#\d+)?\.", key):
        return None
    entry = profile.models.get(_model_id(key))
    if entry is None:
        return "model not covered"
    path = _path(key)
    if path in entry["implemented"]:
        return "implemented"
    if path in entry["not_implemented"]:
        return "unimplemented"
    return "not listed"


_NO_DETAILS = {"certified": None, "min": None, "max": None}


def pics_details(profile: PicsProfile | None, key: str) -> dict[str, Any]:
    """The certified value, Min and Max the PICS gives for one point, each ``None``
    where it gives none. The value is as the test lab recorded it, not scaled."""
    if profile is None or not re.match(r"^\d+(#\d+)?\.", key):
        return dict(_NO_DETAILS)
    found = profile.details.get(_model_id(key), {}).get(_path(key), {})
    return {"certified": found.get("value"), "min": found.get("min"), "max": found.get("max")}


@dataclass
class PicsReport:
    """Where the device and the PICS disagree, and what the PICS did not cover."""

    certified_no_value: list[str] = field(default_factory=list)
    """PICS: implemented. Device: no value on every read. Stays implemented."""
    value_not_certified: list[str] = field(default_factory=list)
    """PICS: unimplemented. Device: gave a value. Becomes implemented."""
    not_in_pics: list[str] = field(default_factory=list)
    """Points of a covered model that the PICS does not list; sorted by discovery."""
    discovered_models: list[int] = field(default_factory=list)
    """Models the PICS does not cover; sorted by discovery."""
    pics_only: list[str] = field(default_factory=list)
    """PICS entries we read no point for (e.g. scale factors, applied elsewhere)."""


def apply_pics(
    discovered: ImplementedPoints, profile: PicsProfile
) -> tuple[ImplementedPoints, PicsReport]:
    """Sort points by the PICS where it covers them, by discovery elsewhere."""
    report = PicsReport()
    implemented: set[str] = set()
    not_implemented: set[str] = set()
    seen_paths: dict[int, set[str]] = {}
    discovered_models: set[int] = set()
    for key in sorted(discovered.implemented | discovered.not_implemented):
        model_id = _model_id(key)
        has_value = key in discovered.implemented
        entry = profile.models.get(model_id)
        if entry is None:
            discovered_models.add(model_id)
            (implemented if has_value else not_implemented).add(key)
            continue
        path = _path(key)
        seen_paths.setdefault(model_id, set()).add(path)
        if path in entry["implemented"]:
            implemented.add(key)
            if not has_value:
                report.certified_no_value.append(key)
        elif path in entry["not_implemented"]:
            if has_value:
                implemented.add(key)
                report.value_not_certified.append(key)
                _LOGGER.info("Point %s gives a value but the PICS says unimplemented", key)
            else:
                not_implemented.add(key)
        else:
            report.not_in_pics.append(key)
            (implemented if has_value else not_implemented).add(key)
    for model_id, entry in sorted(profile.models.items()):
        listed = entry["implemented"] | entry["not_implemented"]
        unread = listed - seen_paths.get(model_id, set())
        report.pics_only += [f"{model_id}.{path}" for path in sorted(unread)]
    report.discovered_models = sorted(discovered_models)
    source = f"PICS {profile.certificate}"
    if report.discovered_models:
        models = ", ".join(map(str, report.discovered_models))
        source += f"; discovered for model {models} ({discovered.source})"
    result = ImplementedPoints(
        source=source,
        implemented=frozenset(implemented),
        not_implemented=frozenset(not_implemented),
        unreadable_models=discovered.unreadable_models,
    )
    return result, report
