"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_10.json)

from __future__ import annotations

from enum import IntEnum

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    enum16,
    uint16,
)


class InterfaceStatus(IntEnum):
    DOWN = 0
    UP = 1
    FAULT = 2


class PhysicalAccessType(IntEnum):
    UNKNOWN = 0
    INTERNAL = 1
    TWISTED_PAIR = 2
    FIBER = 3
    WIRELESS = 4


class Model10(SunSpecComponent):
    """SunSpec model 10: Communication Interface Header."""

    st = enum16(2, InterfaceStatus)
    """Interface Status. Overall interface status."""

    ctl = uint16(3, writable=True)
    """Interface Control. Overall interface control (TBD)."""

    typ = enum16(4, PhysicalAccessType)
    """Physical Access Type. Type of physical media."""
