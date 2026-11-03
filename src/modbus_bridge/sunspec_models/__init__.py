"""The SunSpec model catalogue: official definitions and their generated components.

See SOURCE.md for where the definitions come from and how they are generated.
"""

from __future__ import annotations

import importlib
import inspect
import json
import logging
from enum import Enum, IntEnum
from functools import cache
from importlib import resources
from typing import Any

from modbus_connection.model import Component
from modbus_connection.model.sunspec import SunSpecComponent

_LOGGER = logging.getLogger(__name__)

#: The name given to an enum value that the SunSpec definition does not name.
UNKNOWN = "UNKNOWN"
_LOGGED: set[tuple[type, int]] = set()


def _keep_unknown(cls: type[IntEnum], value: object) -> IntEnum | None:
    """Keep a value the definition does not name, as a pseudo-member called UNKNOWN.

    Without this, modbus-connection would decode it as ``None`` and the point
    would look unimplemented (rule 8: no silent fallbacks).
    """
    if not isinstance(value, int):
        return None
    member = int.__new__(cls, value)
    member._name_ = UNKNOWN
    member._value_ = value
    if (cls, value) in _LOGGED:
        return member
    _LOGGED.add((cls, value))
    _LOGGER.warning(
        "%s: value %d is not named in the SunSpec definition; kept", cls.__name__, value
    )
    return member


def _patch_enums(component: type[Component], done: set[type]) -> None:
    """Give every IntEnum used by this component (and its groups) the fallback above."""
    if component in done:
        return
    done.add(component)
    for field in component.declared_fields.values():
        convert = getattr(field, "convert", None)
        if isinstance(convert, type) and issubclass(convert, IntEnum) and convert not in done:
            convert._missing_ = classmethod(_keep_unknown)
            done.add(convert)
    for group in (*component._static_groups.values(), *component._repeating_fields.values()):
        _patch_enums(group.component_class, done)


@cache
def definition(model_id: int) -> dict[str, Any] | None:
    """Return the official definition of a model, or ``None`` if we have none."""
    path = resources.files(__name__).joinpath("json", f"model_{model_id}.json")
    if not path.is_file():
        return None
    return json.loads(path.read_text())


@cache
def component_class(model_id: int) -> type[SunSpecComponent] | None:
    """Return the generated component for a model, or ``None`` if there is none."""
    try:
        module = importlib.import_module(f"{__name__}.generated.model_{model_id}")
    except ModuleNotFoundError:
        return None
    classes = [
        cls
        for _, cls in inspect.getmembers(module, inspect.isclass)
        if issubclass(cls, SunSpecComponent)
        and cls is not SunSpecComponent
        and cls.__module__ == module.__name__
    ]
    if len(classes) != 1:
        raise RuntimeError(f"model {model_id}: expected one component, found {len(classes)}")
    _patch_enums(classes[0], set())
    return classes[0]


def is_unknown(value: object) -> bool:
    """True for an enum value the SunSpec definition does not name."""
    return isinstance(value, Enum) and value.name == UNKNOWN
